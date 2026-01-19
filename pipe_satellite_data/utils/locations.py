from datetime import datetime
from datetime import timedelta

# Using the library https://pythonhosted.org/spacetrack/usage.html
from spacetrack import SpaceTrackClient

from time import sleep

import ephem
import itertools as it
import pytz
import spacetrack.operators as op
import time
import udatetime
import ujson as json
import logging


EPOCH = udatetime.utcfromtimestamp(0)

SECONDS_IN_DAY=24*60*60


def fetch_TLE(st_auth, norad_ids, dt):
    """
    Fetch TLEs for a set of satellites for a given day, one TLE per day per satellite
    These are retrieved from the API at space-track.org

    :param st_auth: credentials for the SpaceTrack api {'user':'user', 'password':'password'}
    :param norad_ids: list of norad ids for satellites to retrieve locations for
    :param dt: datetime  retrieve a lat,lon location for every second in this day
    :return: list of dicts
    """

    # authenticate to space-track.org API
    st = SpaceTrackClient(identity=st_auth['user'], password=st_auth['password'])

    # remote timezone if present
    dt = dt.replace(tzinfo=None)

    # Retrieve all TLE's for all objects in the norad id list
    logging.info("Retrieving perturbation history")
    response = st.gp_history(
        norad_cat_id=[str(i) for i in norad_ids],
        # We want to order the resulting records by norad id first (to be able
        # to group and process each object separately) and then by epoch
        # descending, so that we can inspect the most recent record for each
        # object.
        order_by='NORAD_CAT_ID asc,EPOCH desc',
        # Fetch any GP records where the epoc is between 7 days before from the
        # target date, and 3 days after it in case a newer record exists but no
        # records exists for the current date
        epoch=op.inclusive_range(dt - timedelta(days=7), dt + timedelta(days=3)),
        format="json",
    )
    logging.info("Parsing response")
    all_perturbations = json.loads(response)

    # Select the best TLE for each object independently
    for norad_id, perturbations in it.groupby(all_perturbations, key=lambda x: x['NORAD_CAT_ID']):
        logging.info("Processing object with norad id {}", norad_id)
        # For each norad id, we have to select the best perturbation for the
        # timestamp we are processing.
        best_perturbation = None

        # We prefer the latest perturbation (the one with the greatest epoch)
        # as long as that epoch is before the target timestamp. However, if
        # there are no records before the target timestamp, then we can use the
        # earliest one after the target timestamp instead.
        perturbations_before_dt = list(it.dropwhile(lambda x: x["EPOCH"] > dt, perturbations))
        perturbations_after_dt = list(it.takewhile(lambda x: x["EPOCH"] > dt, perturbations ))
        best_perturbation = perturbations_before_dt[0] if perturbations_before_dt else perturbations_after_dt[-1]
        logging.info("Best perturbation for this object is {}", best_perturbation)

        # We've found the best perturbation for this object. However, if the
        # best perturbation indicates the satellite decayed, then we need to
        # skip this object
        if best_perturbation["DECAY_DATE"]:
            logging.info("Perturbation is a decay event. Skipping.")
        else:
            logging.info("Best perturbation is not a decay event, yielding for processing")
            yield best_perturbation


def as_timestamp(dt):
    return (pytz.UTC.localize(dt) - EPOCH).total_seconds()


def satellite_locations(tles, dt):
    """
    compute locations for the center of the satellite footprint for the given list of TLEs
    for every second in the given date

    :param tles: list of TLEs retrieved from the space-track.org API (see fetch_TLE())
    :param dt: datetime  retrive a lat,lon location for every second in this day
    :return: list of {norad_id: norad_id, timestamp: datetime, lat: latitude, lon: longitude }
    """

    start_ts = int(as_timestamp(dt) / SECONDS_IN_DAY) * SECONDS_IN_DAY
    end_ts = start_ts + SECONDS_IN_DAY

    for tle in tles:
        try:
            tle_lines = [str(tle['TLE_LINE%s' % i]) for i in range(3)]
            orbit = ephem.readtle(*tle_lines)

            for ts in range(start_ts, end_ts):
                orbit.compute(datetime.utcfromtimestamp(ts).strftime("%Y/%m/%d %H:%M:%S"))
                lon = ephem.degrees(orbit.sublong) * 180 / 3.1416
                lat = ephem.degrees(orbit.sublat) * 180 / 3.1416
                elevation = orbit.elevation

                yield dict(
                    norad_id=tle['NORAD_CAT_ID'],
                    lat=lat,
                    lon=lon,
                    timestamp=ts,
                    altitude=elevation
                )
        except RuntimeError as e:
            logging.error(e, f'Error found in TLE: {tle}.\nCheck satellite status: https://www.n2yo.com/satellite/?s={tle["NORAD_CAT_ID"]}')
            raise e
