import pytest
from streamkit.error_handling import (
    ErrorHandlingFallback,
    ErrorHandlingRetry,
    ErrorHandlingSkip,
    TransientNetworkError,
)

def test_fallback_below_threshold():
    fh = ErrorHandlingFallback(default_value=0, threshold=3)
    with pytest.raises(TimeoutError):
        fh.handle(2)
    assert fh.handle(3) == 0

def test_retry_success(monkeypatch):
    calls = []
    def flaky(x):
        calls.append(1)
        if len(calls) < 2:
            raise TransientNetworkError("fail")
        return x * 2
    er = ErrorHandlingRetry(max_retries=3)
    assert er.execute(flaky, 5) == 10
    assert len(calls) == 2

def test_retry_exhaust(monkeypatch):
    def always_fail():
        raise TransientNetworkError("nope")
    er = ErrorHandlingRetry(max_retries=1)
    with pytest.raises(TransientNetworkError):
        er.execute(always_fail)

def test_skip_stage():
    def is_valid(x):
        return isinstance(x, int) and x > 0
    sk = ErrorHandlingSkip()
    assert sk.process(1, is_valid) == 1
    assert sk.process(-1, is_valid) is None
    assert sk.skipped == [-1]
