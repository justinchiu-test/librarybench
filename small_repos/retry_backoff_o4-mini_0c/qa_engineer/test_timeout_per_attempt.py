import pytest
import time
from retry_toolkit.timeout_per_attempt import timeout_per_attempt, TimeoutError

def test_no_timeout():
    @timeout_per_attempt(1)
    def fast():
        return "done"
    assert fast() == "done"

def test_timeout():
    @timeout_per_attempt(0.1)
    def slow():
        time.sleep(0.2)
        return "late"
    with pytest.raises(TimeoutError):
        slow()
