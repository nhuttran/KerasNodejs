from datetime import datetime
from pytz import timezone
from dateutil import parser
from . import FormatUtils

def get_time_zone(utc_time=None, format=None):
    if not utc_time is None:
        tokyo_tz = parser.parse(utc_time).astimezone(timezone("Asia/Tokyo"))
    else:
        tokyo_tz = datetime.now(timezone("Asia/Tokyo"))

    if format is not None:
        time_zone_str = tokyo_tz.strftime(format)
    else:
        time_zone_str = tokyo_tz.strftime(FormatUtils.FORMAT_TIME_ZONE)
    return time_zone_str