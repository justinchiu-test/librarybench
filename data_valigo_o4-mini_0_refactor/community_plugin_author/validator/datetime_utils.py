from datetime import datetime
import time

def parse_date(date_str: str, fmt: str = None) -> datetime:
    if fmt:
        return datetime.strptime(date_str, fmt)
    # ISO by default
    return datetime.fromisoformat(date_str)

def normalize_timezone(dt: datetime, tzinfo) -> datetime:
    if dt.tzinfo:
        return dt.astimezone(tzinfo)
    return dt.replace(tzinfo=tzinfo)

def min_date(dt: datetime, min_dt: datetime):
    if dt < min_dt:
        raise ValueError(f"Date {dt} is before minimum {min_dt}")
    return dt

def max_date(dt: datetime, max_dt: datetime):
    if dt > max_dt:
        raise ValueError(f"Date {dt} is after maximum {max_dt}")
    return dt
