import pytest
from error_handling import retry_on_exception, fallback

counter = {'count': 0}

@retry_on_exception(retries=2, backoff_seconds=0)
def flaky():
    counter['count'] += 1
    if counter['count'] < 2:
        raise ValueError("fail")
    return "ok"

def test_retry_success():
    counter['count'] = 0
    assert flaky() == "ok"
    assert counter['count'] == 2

@retry_on_exception(retries=1, backoff_seconds=0)
def always_fail():
    raise RuntimeError("always")

def test_retry_exhausted():
    with pytest.raises(RuntimeError):
        always_fail()

@fallback(default_value=42)
def fail_func():
    raise Exception("oops")

def test_fallback():
    assert fail_func() == 42
