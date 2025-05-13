import pytest
import time
from file_watcher.core import ErrorHandler

def test_retry_success_after_failures():
    handler = ErrorHandler(retries=3, backoff_factor=0.01)
    attempts = {'count': 0}
    @handler.retry
    def flaky():
        attempts['count'] += 1
        if attempts['count'] < 3:
            raise ValueError("fail")
        return "ok"
    result = flaky()
    assert result == "ok"
    assert attempts['count'] == 3

def test_retry_exhaustion_raises():
    handler = ErrorHandler(retries=2, backoff_factor=0.01)
    @handler.retry
    def always_fail():
        raise RuntimeError("always")
    with pytest.raises(RuntimeError):
        always_fail()
