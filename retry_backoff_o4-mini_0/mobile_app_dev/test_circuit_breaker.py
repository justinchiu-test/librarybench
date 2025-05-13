import time
import pytest
from retry.circuit_breaker import CircuitBreakerIntegration, CircuitBreakerOpenException

def test_circuit_breaker_opens_and_resets():
    cb = CircuitBreakerIntegration(failure_threshold=2, recovery_timeout=0.1)
    cb.before_call()
    cb.after_call(False)
    assert cb.state == 'CLOSED'
    cb.before_call()
    cb.after_call(False)
    assert cb.state == 'OPEN'
    with pytest.raises(CircuitBreakerOpenException):
        cb.before_call()
    time.sleep(0.2)
    cb.before_call()
    assert cb.state == 'HALF_OPEN'
    cb.after_call(True)
    assert cb.state == 'CLOSED'
