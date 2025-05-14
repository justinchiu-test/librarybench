import pytest
import time
from pipeline.retry import retry_on_error

def test_retry_success():
    calls = {'count': 0}
    @retry_on_error(max_retries=3, base_delay=0.001)
    def flaky():
        calls['count'] += 1
        if calls['count'] < 2:
            raise ValueError("fail")
        return "ok"
    assert flaky() == "ok"
    assert calls['count'] == 2

def test_retry_failure():
    @retry_on_error(max_retries=2, base_delay=0)
    def always_fail():
        raise KeyError("oops")
    with pytest.raises(KeyError):
        always_fail()
