import time
import pytest
from task_queue.circuit_breaker import CircuitBreaker, CircuitOpen

def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    svc = 'downstream'
    assert cb.allow_request(svc)
    cb.record_failure(svc)
    assert cb.allow_request(svc)
    cb.record_failure(svc)
    # now should open
    assert not cb.allow_request(svc)
    with pytest.raises(Exception):
        # simulate check and raise
        if not cb.allow_request(svc):
            raise CircuitOpen
    # wait for recovery
    time.sleep(1.1)
    assert cb.allow_request(svc)
    cb.record_success(svc)
    assert cb.allow_request(svc)
