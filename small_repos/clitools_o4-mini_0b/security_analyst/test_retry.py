import time
import pytest
from cli_framework.retry import retry_call

def test_retry_success(monkeypatch):
    calls = {"count":0}
    def func():
        calls["count"] +=1
        if calls["count"] < 3:
            raise ValueError
        return "ok"
    monkeypatch.setattr(time, "sleep", lambda x: None)
    res = retry_call(func, retries=5, base_delay=0.01)
    assert res == "ok"
    assert calls["count"] == 3

def test_retry_fail(monkeypatch):
    def func():
        raise RuntimeError
    monkeypatch.setattr(time, "sleep", lambda x: None)
    with pytest.raises(RuntimeError):
        retry_call(func, retries=2, base_delay=0.01)
