import time
import pytest
from retry_framework.timeout import timeout_per_attempt, TimeoutError

def test_timeout_decorator_pass():
    @timeout_per_attempt(1)
    def fast():
        time.sleep(0.1)
        return "ok"
    assert fast() == "ok"

def test_timeout_decorator_fail():
    @timeout_per_attempt(0)
    def slow():
        time.sleep(0.1)
    with pytest.raises(TimeoutError):
        slow()
