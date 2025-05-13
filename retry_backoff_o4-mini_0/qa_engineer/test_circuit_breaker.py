import pytest
import time
from retry_toolkit.circuit_breaker import CircuitBreaker

def always_fail():
    raise Exception("fail")

def test_circuit_opens_after_threshold():
    cb = CircuitBreaker(failure_threshold=2, reset_timeout=1)
    with pytest.raises(Exception):
        cb.call(always_fail)
    with pytest.raises(Exception):
        cb.call(always_fail)
    assert cb.is_open
    with pytest.raises(Exception):
        cb.call(always_fail)

def test_circuit_resets_after_timeout():
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=0.1)
    with pytest.raises(Exception):
        cb.call(always_fail)
    assert cb.is_open
    time.sleep(0.2)
    # after timeout, circuit should close
    assert not cb.is_open
    # now should count fresh
    with pytest.raises(Exception):
        cb.call(always_fail)
    assert cb.is_open

def test_reset_method_closes_circuit():
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=10)
    with pytest.raises(Exception):
        cb.call(always_fail)
    assert cb.is_open
    cb.reset()
    assert not cb.is_open
