from datetime import datetime, timezone, timedelta
import pytest
from security_officer.incident_form.fields import DateTimePicker

def test_datetime_picker_naive():
    picker = DateTimePicker(timezone_offset_hours=2)
    dt = datetime(2020,1,1,12,0,0)
    picked = picker.pick(dt)
    assert picked.tzinfo.utcoffset(picked) == timedelta(hours=2)

def test_datetime_picker_with_tz():
    picker = DateTimePicker(timezone_offset_hours=-5)
    dt = datetime(2020,1,1,12,0,0, tzinfo=timezone.utc)
    picked = picker.pick(dt)
    assert picked.tzinfo.utcoffset(picked) == timedelta(hours=-5)

def test_datetime_picker_invalid():
    picker = DateTimePicker()
    with pytest.raises(ValueError):
        picker.pick("not a datetime")
