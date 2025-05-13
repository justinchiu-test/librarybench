import pytest
from datetime import datetime, timedelta
from iotscheduler.utils import (
    enable_daylight_saving_support,
    apply_jitter_and_drift_correction,
    load_plugin,
    register_plugin,
    create_task_group
)

def test_enable_daylight_saving_support():
    # New York DST starts second Sunday in March
    dt = datetime(2021, 3, 14, 2, 30)  # non-existent local time
    adjusted = enable_daylight_saving_support(dt, "America/New_York")
    assert adjusted.tzinfo.zone.endswith("New_York")

def test_apply_jitter_and_drift_correction():
    base = 60.0
    jitter = 5.0
    drift = 2.0
    results = [apply_jitter_and_drift_correction(base, jitter, drift) for _ in range(100)]
    assert all((base - jitter - drift) <= r <= (base + jitter - drift) for r in results)

class DummyPlugin:
    pass

def test_load_and_register_plugin():
    register_plugin("dummy", DummyPlugin)
    plugin = load_plugin("dummy")
    assert plugin is DummyPlugin

def test_create_task_group():
    devices = ["d1", "d2", "d3"]
    grp = create_task_group("test-group", devices)
    assert grp["group_name"] == "test-group"
    assert grp["devices"] == devices
