import pytest
import time
from audit_watcher.errors import resilient

class DummyError(Exception):
    pass

def test_resilient_decorator_success():
    calls = []
    def cb(e, attempt):
        calls.append((str(e), attempt))
    count = {'n': 0}
    @resilient(on_exceptions=(DummyError,), retries=2, backoff_factor=0.01, callback=cb)
    def func():
        count['n'] += 1
        if count['n'] < 2:
            raise DummyError("fail")
        return "ok"
    result = func()
    assert result == "ok"
    assert len(calls) == 1
    assert calls[0][1] == 1

def test_resilient_decorator_exhaust():
    calls = []
    def cb(e, attempt):
        calls.append(attempt)
    @resilient(on_exceptions=(DummyError,), retries=1, backoff_factor=0.01, callback=cb)
    def func2():
        raise DummyError("always")
    with pytest.raises(DummyError):
        func2()
    assert calls == [1]
