import pytest
import time
from retrylib.core import Retry
from retrylib.backoff import ExponentialBackoffStrategy
from retrylib.stop import MaxAttemptsStopCondition
from retrylib.hooks import MetricsHook
from retrylib.context import ContextPropagation
from retrylib.history import RetryHistoryCollector

def test_retry_success_after_retries():
    calls = []
    def flaky():
        calls.append(time.time())
        if len(calls) < 3:
            raise ValueError("fail")
        return "ok"

    strategy = ExponentialBackoffStrategy(initial_delay=0.01, max_delay=0.01)
    stop = MaxAttemptsStopCondition(5)
    metrics = MetricsHook()
    history = RetryHistoryCollector()
    ctx = ContextPropagation(task="test")
    retry_flaky = Retry(strategy, stop, hooks=[metrics], context=ctx, history_collector=history)(flaky)

    result = retry_flaky()

    assert result == "ok"
    assert len(calls) == 3
    assert metrics.attempts == 2
    assert len(history.attempts) == 2
    for rec in history.attempts:
        assert rec['context'].get('task') == "test"

def test_retry_exceeds_max_attempts():
    def always_fail():
        raise RuntimeError("always")

    strategy = ExponentialBackoffStrategy(initial_delay=0.001, max_delay=0.001)
    stop = MaxAttemptsStopCondition(2)
    retry_always = Retry(strategy, stop)(always_fail)
    with pytest.raises(RuntimeError):
        retry_always()
