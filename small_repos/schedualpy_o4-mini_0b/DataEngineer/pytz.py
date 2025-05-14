# A minimal pytz replacement using the stdlib zoneinfo
import datetime
from zoneinfo import ZoneInfo

class timezone(ZoneInfo):
    """
    A thin wrapper around zoneinfo.ZoneInfo to mimic pytz.timezone,
    also ensuring this class is a tzinfo subclass for datetime.
    """
    def __new__(cls, name: str):
        # Use ZoneInfo's __new__ to construct an instance of our subclass
        obj = super().__new__(cls, name)
        return obj

    def __init__(self, name: str):
        # ZoneInfo __init__ does nothing meaningful; we set .zone for pytz compatibility
        self.zone = name

    def utcoffset(self, dt):
        return super().utcoffset(dt)

    def dst(self, dt):
        return super().dst(dt)

    def tzname(self, dt):
        return super().tzname(dt)

    def __repr__(self):
        return f"<DstTzInfo {self.zone}>"

    def __eq__(self, other):
        return isinstance(other, timezone) and getattr(other, "zone", None) == self.zone

# commonly‐used alias
utc = timezone("UTC")
