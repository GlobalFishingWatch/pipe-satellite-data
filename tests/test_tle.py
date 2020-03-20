from datetime import datetime, timedelta
# Using the library https://pythonhosted.org/spacetrack/usage.html
from spacetrack import SpaceTrackClient
import ephem
import itertools as it
import pytz
import spacetrack.operators as op
import time
import udatetime
import ujson as json
from dateutil.parser import parse as dateutil_parse

EPOCH = udatetime.utcfromtimestamp(0)
SECONDS_IN_DAY=24*60*60

def mycallback(until):
    duration = int(round(until - time.time()))
    print(('Sleeping for {:d} seconds.'.format(duration)))

st = SpaceTrackClient(identity='matu.ppp.46@gmail.com', password='Estoesunaprueba')
st.callback = mycallback
dt = dateutil_parse('2019-01-10').replace(tzinfo=None)
norad_ids = ['42841']
days_before=0
decay_epoch = op.inclusive_range((dt + timedelta(- days_before)), (dt + timedelta(3 - days_before)))
print(('Decay_epoch: {}'.format(decay_epoch)))
response = st.tle(norad_cat_id=','.join(norad_ids), orderby='NORAD_CAT_ID', format='json', epoch=decay_epoch)
tle_list = json.loads(response)
print(('Norad_id<{}> has {} TLEs quering epoch <{}>'.format(norad_ids,len(tle_list),decay_epoch)))
