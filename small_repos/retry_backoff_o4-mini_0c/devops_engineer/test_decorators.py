import time
import pytest
from retry_framework.decorators import retry
from retry_framework.history import RetryHistoryCollector
from retry_framework.stop_conditions import MaxAttemptsStopCondition
from retry_framework.cancellation import CancellationPolicy
from retry_framework.circuit_breaker import CircuitBreaker

count = 0
def flaky():
    global count
    count += 1
    if count < 2:
        raise ValueError("fail")
    return 'ok'

def test_retry_success():
    global count
    count = 0
    func = retry(attempts=3, backoff='exponential')(flaky)
    assert func() == 'ok'

def test_retry_history_and_stop_condition():
    global count
    count = 0
    hist = RetryHistoryCollector()
    stop = MaxAttemptsStopCondition(1)
    func = retry(attempts=3, backoff='exponential', stop_condition=stop, history_collector=hist)(flaky)
    with pytest.raises(ValueError):
        func()
    assert len(hist.attempts) == 1

def test_retry_with_cancellation():
    global count
    count = 0
    cp = CancellationPolicy()
    cp.cancel()
    func = retry(attempts=3, backoff='exponential', cancellation_policy=cp)(flaky)
    with pytest.raises(ValueError):
        func()

def test_retry_with_circuit_breaker():
    global count
    count = 0
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
    func = retry(attempts=2, backoff='exponential', circuit_breaker=cb)(flaky)
    result = func()
    assert result == 'ok'
