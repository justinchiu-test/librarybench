import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from unified.src.security_specialist.securedata.datetime_validation import DateTimeValidator

def test_parse_iso():
    dt = DateTimeValidator.parse('2020-01-01T12:00:00')
    assert isinstance(dt, datetime)
    assert dt.year == 2020

def test_parse_custom():
    dt = DateTimeValidator.parse('01/02/2020', '%d/%m/%Y')
    assert dt.day == 1 and dt.month == 2

def test_normalize_naive():
    dt = datetime(2020,1,1,0,0)
    ndt = DateTimeValidator.normalize(dt, 'UTC')
    assert ndt.tzinfo == ZoneInfo('UTC')

def test_normalize_aware():
    dt = datetime(2020,1,1,0,0, tzinfo=ZoneInfo('UTC'))
    ndt = DateTimeValidator.normalize(dt, 'UTC')
    assert ndt.hour == 0 and ndt.tzinfo == ZoneInfo('UTC')

def test_validate_range():
    dt = datetime(2020,1,1,0,0)
    min_dt = datetime(2019,1,1,0,0)
    max_dt = datetime(2021,1,1,0,0)
    assert DateTimeValidator.validate_range(dt, min_dt, max_dt)
    assert not DateTimeValidator.validate_range(dt, datetime(2021,1,1), None)
