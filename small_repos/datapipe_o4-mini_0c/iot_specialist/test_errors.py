import pytest
from telemetry.errors import skip_on_error, failed_devices

def test_valid_reading():
    failed_devices.clear()
    assert skip_on_error("dev1", 10, min_val=0, max_val=100) is True
    assert failed_devices == []

def test_missing_reading():
    failed_devices.clear()
    assert skip_on_error("dev2", None) is False
    assert "dev2" in failed_devices

def test_out_of_range():
    failed_devices.clear()
    assert skip_on_error("dev3", -5, min_val=0) is False
    assert skip_on_error("dev4", 200, max_val=100) is False
    assert set(failed_devices) == {"dev3", "dev4"}
