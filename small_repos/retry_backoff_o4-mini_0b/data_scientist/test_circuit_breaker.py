import time
import pytest
from retry_engine.circuit_breaker import CircuitBreakerIntegration, CircuitOpenException

def test_circuit_breaker_opens_and_recovers(monkeypatch):
    cb = CircuitBreakerIntegration(failure_threshold=2, recovery_timeout=1)
    # First failure
    cb.after_call(False)
    assert cb.failure_count == 1
    # Second failure opens circuit
    cb.after_call(False)
    assert cb.failure_count == 2
    assert cb.opened_at is not None
    # before_call should raise while open
    with pytest.raises(CircuitOpenException):
        cb.before_call()
    # After timeout, should reset
    monkeypatch.setattr(time, 'time', lambda: cb.opened_at + 2)
    cb.before_call()  # no exception
    assert cb.failure_count == 0
    assert cb.opened_at is None
