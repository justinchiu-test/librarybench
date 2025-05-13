import pytest
from retrylib.context import retry_context
from retrylib.backoff import ExponentialBackoffStrategy
from retrylib.stop_conditions import MaxAttemptsStopCondition

def test_successful_retry_attempts(monkeypatch):
    calls = {'count': 0}
    def func():
        calls['count'] += 1
        if calls['count'] < 3:
            raise ValueError("fail")
        return "ok"

    monkeypatch.setattr('time.sleep', lambda x: None)

    after_attempts = []
    retries = []
    giveups = []

    def after_attempt(attempt, exception, result):
        after_attempts.append((attempt, exception, result))

    def on_retry(attempt, delay):
        retries.append((attempt, delay))

    def on_giveup(attempt, exception):
        giveups.append((attempt, exception))

    strategy = ExponentialBackoffStrategy(base=0.1)
    stop_cond = MaxAttemptsStopCondition(max_attempts=5)

    ctx = retry_context(
        backoff_strategy=strategy,
        stop_condition=stop_cond,
        on_retry_hook=on_retry,
        after_attempt_hook=after_attempt,
        on_giveup_hook=on_giveup
    )
    with ctx:
        result = ctx.attempt(func)

    assert result == "ok"
    assert len(after_attempts) == 3
    assert isinstance(after_attempts[0][1], ValueError) and after_attempts[0][2] is None
    assert after_attempts[-1][1] is None and after_attempts[-1][2] == "ok"
    assert len(retries) == 2
    assert giveups == []

def test_retry_exhaustion(monkeypatch):
    def func():
        raise RuntimeError("nope")

    monkeypatch.setattr('time.sleep', lambda x: None)

    after_attempts = []
    retries = []
    giveups = []

    def after_attempt(attempt, exception, result):
        after_attempts.append((attempt, exception, result))

    def on_retry(attempt, delay):
        retries.append((attempt, delay))

    def on_giveup(attempt, exception):
        giveups.append((attempt, exception))

    strategy = ExponentialBackoffStrategy(base=0)
    stop_cond = MaxAttemptsStopCondition(max_attempts=2)

    ctx = retry_context(
        backoff_strategy=strategy,
        stop_condition=stop_cond,
        on_retry_hook=on_retry,
        after_attempt_hook=after_attempt,
        on_giveup_hook=on_giveup
    )
    with ctx:
        with pytest.raises(RuntimeError):
            ctx.attempt(func)

    assert len(after_attempts) == 2
    assert len(retries) == 1
    assert len(giveups) == 1
    assert giveups[0][0] == 2
    assert isinstance(giveups[0][1], RuntimeError)
