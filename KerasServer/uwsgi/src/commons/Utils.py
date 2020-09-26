from datetime import datetime
from pytz import timezone
from dateutil import parser
import json
import functools
from flask import make_response, jsonify, request
from . import EnvConfig

def get_time_zone(utc_time=None, format=None):
    if not utc_time is None:
        tokyo_tz = parser.parse(utc_time).astimezone(timezone("Asia/Tokyo"))
    else:
        tokyo_tz = datetime.now(timezone("Asia/Tokyo"))

    if format is not None:
        time_zone_str = tokyo_tz.strftime(format)
    else:
        time_zone_str = tokyo_tz.strftime(EnvConfig.FORMAT_TIME_ZONE)
    return time_zone_str

# check content-type decorator
def content_type(value):
    def _content_type(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not request.headers.get("Content-Type") == value:
                error_message = {
                    "error": "not supported Content-Type"
                }
                return make_response(jsonify(error_message), 400)

            return func(*args, **kwargs)
        return wrapper
    return _content_type

if __name__ == "__main__":
    pass