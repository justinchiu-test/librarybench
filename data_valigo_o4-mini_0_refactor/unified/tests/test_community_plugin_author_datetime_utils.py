import pytest
from datetime import datetime, timezone, timedelta
from unified.src.community_plugin_author.validator.datetime_utils import parse_date, normalize_timezone, min_date, max_date

def test_parse_iso():
    dt = parse_date('2021-01-02T03:04:05')
    assert dt == datetime(2021,1,2,3,4,5)

def test_parse_custom():
    dt = parse_date('01/02/2021', fmt='%m/%d/%Y')
    assert dt == datetime(2021,1,2)

def test_normalize_timezone():
    dt = datetime(2021,1,1,12,0)
    tz = timezone(timedelta(hours=5))
    ndt = normalize_timezone(dt, tz)
    assert ndt.tzinfo == tz

def test_min_date_ok_and_fail():
    dt = datetime(2021,1,1)
    min_dt = datetime(2020,1,1)
    assert min_date(dt, min_dt) == dt
    with pytest.raises(ValueError):
        min_date(datetime(2019,1,1), min_dt)

def test_max_date_ok_and_fail():
    dt = datetime(2021,1,1)
    max_dt = datetime(2022,1,1)
    assert max_date(dt, max_dt) == dt
    with pytest.raises(ValueError):
        max_date(datetime(2023,1,1), max_dt)
