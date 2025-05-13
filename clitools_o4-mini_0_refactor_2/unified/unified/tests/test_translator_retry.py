import pytest
from adapters.translator.retry import retry

def test_retry_success_after_failure():
    calls = []
    @retry(max_retries=3, base_delay=0, backoff=1, jitter=0)
    def flaky():
        calls.append(1)
        if len(calls) < 2:
            raise ValueError("fail")
        return "ok"
    assert flaky() == "ok"
    assert len(calls) == 2

def test_retry_exhausts_and_raises():
    @retry(max_retries=2, base_delay=0, backoff=1, jitter=0)
    def always_fail():
        raise RuntimeError("bad")
    with pytest.raises(RuntimeError):
        always_fail()