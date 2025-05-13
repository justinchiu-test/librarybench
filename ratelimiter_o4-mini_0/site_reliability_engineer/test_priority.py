import pytest
from rate_limiter.priority import assign_priority_bucket, get_priority

def test_assign_and_get_priority():
    assert assign_priority_bucket("task", 5) is True
    assert get_priority("task") == 5
    assert get_priority("unknown") is None
