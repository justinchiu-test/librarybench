import pytest
from fintech_developer.circuit_breaker import CircuitBreaker, CircuitOpen

def test_circuit_breaker_opens_after_failures():
    cb = CircuitBreaker(failure_threshold=2)
    def failer():
        raise ValueError("fail")
    with pytest.raises(ValueError):
        cb.call(failer)
    with pytest.raises(ValueError):
        cb.call(failer)
    assert cb.is_open()
    with pytest.raises(CircuitOpen):
        cb.call(lambda: True)
    cb.reset()
    assert not cb.is_open()
    assert cb.call(lambda: 1) == 1
