import pytest
import time
from retry_toolkit.circuit_breaker import CircuitBreaker, CircuitOpenException

def test_circuit_breaker_open_close():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    def fail():
        raise ValueError("err")
    with pytest.raises(ValueError):
        cb.call(fail)
    with pytest.raises(ValueError):
        cb.call(fail)
    with pytest.raises(CircuitOpenException):
        cb.call(lambda: None)
    time.sleep(1.1)
    called = {'ok': False}
    def succeed():
        called['ok'] = True
        return "ok"
    result = cb.call(succeed)
    assert result == "ok"
    assert called['ok']
    # then closed
    called['ok'] = False
    result = cb.call(succeed)
    assert result == "ok"
    assert called['ok']
