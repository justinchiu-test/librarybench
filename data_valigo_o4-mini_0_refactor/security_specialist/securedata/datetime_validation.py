from datetime import datetime
from zoneinfo import ZoneInfo

class DateTimeValidator:
    @staticmethod
    def parse(date_str: str, fmt: str = None):
        if fmt:
            return datetime.strptime(date_str, fmt)
        return datetime.fromisoformat(date_str)

    @staticmethod
    def normalize(dt: datetime, tz: str = 'UTC'):
        zone = ZoneInfo(tz)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=zone)
        return dt.astimezone(zone)

    @staticmethod
    def validate_range(dt: datetime, min_dt=None, max_dt=None):
        if min_dt and dt < min_dt:
            return False
        if max_dt and dt > max_dt:
            return False
        return True
