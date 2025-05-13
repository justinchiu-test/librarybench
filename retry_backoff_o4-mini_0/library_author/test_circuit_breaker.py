import time
import pytest
from retry_framework.circuit_breaker import CircuitBreakerIntegration

def test_circuit_breaker_closed_by_default():
    cb = CircuitBreakerIntegration(max_failures=2, reset_timeout=1)
    assert not cb.is_open

def test_opens_after_failures():
    cb = CircuitBreakerIntegration(max_failures=2, reset_timeout=1)
    cb.record_failure()
    assert not cb.is_open
    cb.record_failure()
    assert cb.is_open

def test_resets_after_success():
    cb = CircuitBreakerIntegration(max_failures=1, reset_timeout=1)
    cb.record_failure()
    assert cb.is_open
    cb.record_success()
    assert not cb.is_open

def test_half_open_after_timeout():
    cb = CircuitBreakerIntegration(max_failures=1, reset_timeout=0)
    cb.record_failure()
    assert cb.is_open
    time.sleep(0.01)
    # elapsed >= reset_timeout, should reset
    assert not cb.is_open
