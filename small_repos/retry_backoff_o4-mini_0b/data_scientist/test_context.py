import pytest
import time
from retry_engine.context import retry_context
from retry_engine.circuit_breaker import CircuitOpenException
from retry_engine.backoff import ExponentialBackoffStrategy
from retry_engine.stop_conditions import MaxAttemptsStopCondition

def test_success_after_retries(monkeypatch):
    # Simulate function that fails twice then succeeds
    calls = {'count': 0}
    def flaky():
        calls['count'] += 1
        if calls['count'] < 3:
            raise ValueError("fail")
        return "ok"

    retries = []
    afters = []
    gives = []
    def on_retry(attempt, delay):
        retries.append((attempt, delay))
    def after_attempt(attempt, success, exception):
        afters.append((attempt, success, isinstance(exception, Exception)))
    def on_give_up(attempt, exception):
        gives.append((attempt, exception))

    start = time.time()
    with retry_context(
        backoff_strategy=ExponentialBackoffStrategy(base=0.01, max_delay=0.01),
        stop_condition=MaxAttemptsStopCondition(5),
        on_retry=on_retry,
        after_attempt=after_attempt,
        on_give_up=on_give_up
    ) as ctx:
        result = ctx.call(flaky)
    assert result == "ok"
    assert calls['count'] == 3
    # Two retries should have been scheduled
    assert len(retries) == 2
    # after_attempt called three times
    assert len(afters) == 3
    # on_give_up never called
    assert gives == []

def test_give_up_after_max(monkeypatch):
    # Function always fails
    def always_fail():
        raise RuntimeError("bad")

    retries = []
    afters = []
    gives = []
    def on_retry(attempt, delay):
        retries.append(attempt)
    def after_attempt(attempt, success, exception):
        afters.append((attempt, success))
    def on_give_up(attempt, exception):
        gives.append((attempt, isinstance(exception, RuntimeError)))

    with pytest.raises(RuntimeError):
        with retry_context(
            backoff_strategy=ExponentialBackoffStrategy(base=0.0),
            stop_condition=MaxAttemptsStopCondition(3),
            on_retry=on_retry,
            after_attempt=after_attempt,
            on_give_up=on_give_up
        ) as ctx:
            ctx.call(always_fail)
    # Retries 2 times before giving up on 3rd attempt
    assert retries == [1, 2]
    assert afters == [(1, False), (2, False), (3, False)]
    assert gives == [(3, True)]

def test_circuit_breaker_bypass(monkeypatch):
    # Circuit that opens immediately
    class DummyCB:
        def before_call(self):
            raise CircuitOpenException()
        def after_call(self, success):
            pass
    def dummy():
        return "x"
    with pytest.raises(CircuitOpenException):
        with retry_context(circuit_breaker=DummyCB()) as ctx:
            ctx.call(dummy)
