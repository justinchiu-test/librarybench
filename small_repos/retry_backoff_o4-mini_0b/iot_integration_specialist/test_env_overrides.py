import os
from retrylib.context import retry_context
from retrylib.backoff import ExponentialBackoffStrategy
from retrylib.stop_conditions import MaxAttemptsStopCondition
from retrylib.env import EnvVarOverrides

def test_env_overrides(monkeypatch):
    monkeypatch.setenv('RETRY_MAX_ATTEMPTS', '3')
    monkeypatch.setenv('RETRY_BASE', '5')
    monkeypatch.setenv('RETRY_CAP', '7')

    strategy = ExponentialBackoffStrategy(base=1, cap=2)
    stop_cond = MaxAttemptsStopCondition(max_attempts=2)
    env = EnvVarOverrides(prefix='RETRY')

    ctx = retry_context(
        backoff_strategy=strategy,
        stop_condition=stop_cond,
        env_overrides=env
    )

    assert ctx.backoff_strategy.base == 5.0
    assert ctx.backoff_strategy.cap == 7.0
    assert ctx.stop_condition.max == 3
