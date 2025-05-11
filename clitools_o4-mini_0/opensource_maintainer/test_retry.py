from osscli.retry import retry_call
import pytest
def test_retry_success_after_fail():
    calls = []
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ValueError("fail")
        return "ok"
    wrapped = retry_call(tries=5, backoff=0)(flaky)
    assert wrapped() == "ok"
    assert len(calls) == 3
def test_retry_exhaust():
    def always_fail():
        raise RuntimeError
    wrapped = retry_call(tries=2, backoff=0)(always_fail)
    with pytest.raises(RuntimeError):
        wrapped()
