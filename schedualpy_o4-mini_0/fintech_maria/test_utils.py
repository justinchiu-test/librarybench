import pytest
import datetime
import pytz
from scheduler.utils import enable_daylight_saving_support, apply_jitter_and_drift_correction, calculate_drift

def test_enable_daylight_saving_support_est():
    # US/Eastern DST date: July 1st
    dt = enable_daylight_saving_support((16, 0), 'US/Eastern')
    assert dt.hour == 16 and dt.minute == 0
    assert dt.tzinfo.zone == 'US/Eastern'

def test_apply_jitter_and_drift_correction():
    base = 10
    jitter = 5
    for _ in range(10):
        val = apply_jitter_and_drift_correction(base, jitter)
        assert base <= val <= base + jitter

def test_calculate_drift():
    t1 = datetime.datetime.now()
    t2 = t1 + datetime.timedelta(seconds=2.5)
    drift = calculate_drift(t1, t2)
    assert abs(drift - 2.5) < 0.001
