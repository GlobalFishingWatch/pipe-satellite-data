from datetime import datetime
from datetime import timedelta
import ujson as json
import itertools as it

import pytz
import udatetime

import ephem
from spacetrack import SpaceTrackClient
import spacetrack.operators as op


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
    st.callback = mycallback

    # remote timezone if present
    dt = dt.replace(tzinfo=None)

    # Search from the given date and 3 days ahead, in case there is no data for our target date
    decay_epoch = op.inclusive_range(dt, (dt + timedelta(3)))

    norad_ids = [str(i) for i in norad_ids]

    # retrieve potentially multiple TLEs for each norad_id

    if norad_ids:
        response = st.tle(norad_cat_id=','.join(norad_ids), orderby='NORAD_CAT_ID', format='json', epoch=decay_epoch)

        tle_list = json.loads(response)

        # filter to just one TLE per norad_id
        for norad_id, tles in it.groupby(tle_list, key=lambda x: x['NORAD_CAT_ID']):
            # take the first one which will be the earliest timestamp
            yield list(tles)[0]

def mycallback(until):
    duration = int(round(until - time.time()))
    print(('Sleeping for {:d} seconds.'.format(duration)))

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
