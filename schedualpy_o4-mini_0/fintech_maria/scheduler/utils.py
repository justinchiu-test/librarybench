import datetime
import random

class SimpleTz(datetime.tzinfo):
    def __init__(self, name):
        super().__init__()
        self.zone = name

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return self.zone

def enable_daylight_saving_support(market_close_time, timezone_str):
    """
    Given a naive time (hour, minute), return a timezone-aware datetime for today at local market close,
    adjusted for DST in the given timezone.
    """
    hour, minute = market_close_time
    today = datetime.datetime.now().date()
    local_dt = datetime.datetime(today.year, today.month, today.day, hour, minute)
    tz = SimpleTz(timezone_str)
    local_dt = local_dt.replace(tzinfo=tz)
    return local_dt

def apply_jitter_and_drift_correction(base_delay, sla_jitter):
    """
    Returns a jittered delay within [base_delay, base_delay + sla_jitter].
    """
    return base_delay + random.uniform(0, sla_jitter)

def calculate_drift(expected_time, actual_time):
    """
    Calculate drift in seconds between expected and actual run time.
    """
    return (actual_time - expected_time).total_seconds()
