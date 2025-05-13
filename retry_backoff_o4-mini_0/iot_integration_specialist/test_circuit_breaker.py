import pytest
from retrylib.context import retry_context
from retrylib.backoff import ExponentialBackoffStrategy
from retrylib.stop_conditions import MaxAttemptsStopCondition
from retrylib.circuit_breaker import CircuitBreaker, CircuitOpenException

def test_circuit_breaker_opens(monkeypatch):
    def func():
        raise ValueError("err")

    monkeypatch.setattr('time.sleep', lambda x: None)

    after_attempts = []
    giveups = []

    def after_attempt(attempt, exception, result):
        after_attempts.append((attempt, exception, result))

    def on_giveup(attempt, exception):
        giveups.append((attempt, exception))

    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=10)
    strategy = ExponentialBackoffStrategy(base=0)
    stop_cond = MaxAttemptsStopCondition(max_attempts=5)

    ctx = retry_context(
        backoff_strategy=strategy,
        stop_condition=stop_cond,
        circuit_breaker=cb,
        after_attempt_hook=after_attempt,
        on_giveup_hook=on_giveup
    )
    with ctx:
        with pytest.raises(CircuitOpenException):
            ctx.attempt(func)

    assert len(after_attempts) == 2
    assert len(giveups) == 1
    assert giveups[0][0] == 3
    assert isinstance(giveups[0][1], CircuitOpenException)
