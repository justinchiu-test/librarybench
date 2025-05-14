import time
from data_engineer.etl.circuitbreaker import CircuitBreaker

def test_circuit_breaker_allows_and_blocks():
    cb = CircuitBreaker(failure_threshold=2, reset_timeout=1)
    name = "api"
    assert cb.can_retry(name)
    cb.record_failure(name)
    assert cb.can_retry(name)
    cb.record_failure(name)
    assert not cb.can_retry(name)
    time.sleep(1.1)
    assert cb.can_retry(name)
    cb.record_success(name)
    assert cb.can_retry(name)
