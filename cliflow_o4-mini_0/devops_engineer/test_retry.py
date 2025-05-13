import pytest
from cli_framework.retry import retry

def test_retry_success():
    calls = {'count': 0}
    @retry(times=3, delay=0, backoff=1)
    def f():
        calls['count'] += 1
        if calls['count'] < 2:
            raise ValueError("fail")
        return "ok"
    assert f() == "ok"
    assert calls['count'] == 2

def test_retry_failure():
    @retry(times=2, delay=0, backoff=1)
    def f():
        raise RuntimeError("bad")
    with pytest.raises(RuntimeError):
        f()
