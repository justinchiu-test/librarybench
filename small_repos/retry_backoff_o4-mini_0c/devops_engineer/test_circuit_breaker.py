import pytest
import time
from retry_framework.circuit_breaker import CircuitBreaker, CircuitBreakerOpen

def always_fail():
    raise RuntimeError('fail')

def always_succeed():
    return 'ok'

def test_circuit_breaker_open_and_recovery():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    with pytest.raises(RuntimeError):
        cb.call(always_fail)
    with pytest.raises(RuntimeError):
        cb.call(always_fail)
    # circuit should now open
    with pytest.raises(CircuitBreakerOpen):
        cb.call(always_succeed)
    # wait for recovery
    time.sleep(1.1)
    # should succeed now
    assert cb.call(always_succeed) == 'ok'
