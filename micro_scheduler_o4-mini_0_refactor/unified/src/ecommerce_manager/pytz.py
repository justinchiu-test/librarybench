"""Stub pytz module for eCommerce Manager domain."""
from datetime import timezone as _timezone
from zoneinfo import ZoneInfo

# UTC timezone
utc = _timezone.utc

def timezone(name):
    """Return a timezone-like object with localize support."""
    try:
        tz = ZoneInfo(name)
    except Exception:
        tz = _timezone.utc
    class TzWrapper:
        def __init__(self, tzinfo):
            self._tz = tzinfo
            self.utc = _timezone.utc
        def localize(self, dt):
            return dt.replace(tzinfo=self._tz)
        def __getattr__(self, item):
            return getattr(self._tz, item)
    return TzWrapper(tz)