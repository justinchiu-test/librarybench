"""
Minimal pytz compatibility module for E-commerce Manager.
"""
import datetime
from zoneinfo import ZoneInfo

class TzWrapper(datetime.tzinfo):
    def __init__(self, tzinfo):
        self._tz = tzinfo
    def utcoffset(self, dt):
        return self._tz.utcoffset(dt)
    def dst(self, dt):
        return self._tz.dst(dt)
    def tzname(self, dt):
        return self._tz.tzname(dt)
    def localize(self, dt):
        return dt.replace(tzinfo=self)

def timezone(name):
    tz = ZoneInfo(name)
    return TzWrapper(tz)

utc = timezone('UTC')