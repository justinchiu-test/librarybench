from datetime import datetime
import zoneinfo

class ZoneInfo(zoneinfo.ZoneInfo):
    """A small subclass of zoneinfo.ZoneInfo that adds a .zone property
       (for compatibility with pytz-like interfaces)."""
    @property
    def zone(self):
        return self.key

class DateTimeValidator:
    @staticmethod
    def parse(date_str: str, fmt: str = None, tz: str = None) -> datetime:
        if fmt:
            dt = datetime.strptime(date_str, fmt)
        else:
            dt = datetime.fromisoformat(date_str)
        if tz:
            tzinfo = ZoneInfo(tz)
            dt = dt.replace(tzinfo=tzinfo)
        return dt

    @staticmethod
    def normalize(dt: datetime, tz: str) -> datetime:
        # prepare target timezone
        target_tz = ZoneInfo(tz)
        # if naive, assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        return dt.astimezone(target_tz)

    @staticmethod
    def check_min_max(dt: datetime, min_dt: datetime = None, max_dt: datetime = None) -> bool:
        if min_dt is not None and dt < min_dt:
            return False
        if max_dt is not None and dt > max_dt:
            return False
        return True
