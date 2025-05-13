import pytest
from onboarding.retry import retry

def test_retry_success():
    calls = {'count': 0}
    @retry(max_attempts=3, initial_delay=0, backoff=1)
    def flaky():
        calls['count'] += 1
        if calls['count'] < 2:
            raise ValueError("fail")
        return "ok"
    assert flaky() == "ok"
    assert calls['count'] == 2

def test_retry_fail():
    @retry(max_attempts=2, initial_delay=0, backoff=1)
    def always_fail():
        raise RuntimeError("fail")
    with pytest.raises(RuntimeError):
        always_fail()
