from datetime import datetime, timedelta

from dateutil.parser import parse as dateutil_parse

from spacetrack import SpaceTrackClient

import ephem
import itertools as it
import pytz
import spacetrack.operators as op
import time
import udatetime
import ujson as json

EPOCH = udatetime.utcfromtimestamp(0)
SECONDS_IN_DAY=24*60*60

class TestSpaceTrackClient:
    def assert_properties_in_common(self, tle):
        assert tle["COMMENT"] == "GENERATED VIA SPACETRACK.ORG API"
        assert tle["ORIGINATOR"] == "18 SPCS"
        assert tle["NORAD_CAT_ID"] == "42841"
        assert tle["OBJECT_NAME"] == "LEMUR 2 PETERG"
        assert tle["OBJECT_TYPE"] == "PAYLOAD"
        assert tle["CLASSIFICATION_TYPE"] == "U"
        assert tle["INTLDES"] == "17042S"

    def mycallback(self, until):
        duration = int(round(until - time.time()))
        print(('Sleeping for {:d} seconds.'.format(duration)))

    def test_spacetrackclient(self):
        st = SpaceTrackClient(identity='matu.ppp.46@gmail.com', password='Estoesunaprueba')
        st.callback = self.mycallback

        norad_ids = ['42841']
        days_before=0
        dt = dateutil_parse('2019-01-10').replace(tzinfo=None)
        decay_epoch = op.inclusive_range((dt + timedelta(- days_before)), (dt + timedelta(3 - days_before)))
        assert '2019-01-10 00:00:00--2019-01-13 00:00:00', decay_epoch

        response = st.tle(norad_cat_id=','.join(norad_ids), orderby='NORAD_CAT_ID', format='json', epoch=decay_epoch)
        tle_list = json.loads(response)

        assert 7 == len(tle_list)
        map(lambda x: self.assert_properties_in_common(x), tle_list)
