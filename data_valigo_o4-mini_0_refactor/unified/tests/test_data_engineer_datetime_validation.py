import pytest
from datetime import datetime
from unified.src.data_engineer import DateTimeValidator

def test_iso_parse_and_normalize():
    dt = DateTimeValidator.parse('2020-01-01T12:00:00')
    assert dt == datetime(2020,1,1,12,0,0)
    dt2 = DateTimeValidator.parse('2020-01-01 09:00:00', fmt='%Y-%m-%d %H:%M:%S', tz='UTC')
    assert dt2.tzinfo.zone == 'UTC'
    norm = DateTimeValidator.normalize(dt2, 'Asia/Tokyo')
    assert norm.tzinfo.zone == 'Asia/Tokyo'

def test_min_max():
    dt = DateTimeValidator.parse('2020-01-01T00:00:00')
    past = datetime(2019,12,31)
    future = datetime(2021,1,1)
    assert DateTimeValidator.check_min_max(dt, min_dt=past, max_dt=future)
    assert not DateTimeValidator.check_min_max(dt, min_dt=future)
    assert not DateTimeValidator.check_min_max(dt, max_dt=past)
