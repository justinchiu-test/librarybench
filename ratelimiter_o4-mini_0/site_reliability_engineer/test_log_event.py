import pytest
from rate_limiter.logging import LOGS, log_event

def test_log_event_appends():
    LOGS.clear()
    entry = log_event("test_action", "allow", {"k": "v"})
    assert entry in LOGS
    assert entry["action"] == "test_action"
    assert entry["decision"] == "allow"
    assert entry["metadata"] == {"k": "v"}

def test_log_event_default_metadata():
    LOGS.clear()
    entry = log_event("act", "throttle")
    assert entry["metadata"] == {}
