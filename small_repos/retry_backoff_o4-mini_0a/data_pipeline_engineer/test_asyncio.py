import pytest
import time
from retrylib.asyncio import AsyncRetry
from retrylib.backoff import ExponentialBackoffStrategy
from retrylib.stop import MaxAttemptsStopCondition
from retrylib.hooks import MetricsHook
from retrylib.context import ContextPropagation
from retrylib.history import RetryHistoryCollector

@pytest.mark.asyncio
async def test_async_retry_success_after_retries():
    calls = []
    async def flaky():
        calls.append(time.time())
        if len(calls) < 2:
            raise ValueError("fail")
        return "ok"

    strategy = ExponentialBackoffStrategy(initial_delay=0.01, max_delay=0.01)
    stop = MaxAttemptsStopCondition(5)
    metrics = MetricsHook()
    history = RetryHistoryCollector()
    ctx = ContextPropagation(task="async_test")
    retry_flaky = AsyncRetry(strategy, stop, hooks=[metrics], context=ctx, history_collector=history)(flaky)

    result = await retry_flaky()

    assert result == "ok"
    assert len(calls) == 2
    assert metrics.attempts == 1
    assert len(history.attempts) == 1
    for rec in history.attempts:
        assert rec['context'].get('task') == "async_test"

@pytest.mark.asyncio
async def test_async_retry_exceeds_max_attempts():
    async def always_fail():
        raise RuntimeError("always async")

    strategy = ExponentialBackoffStrategy(initial_delay=0.001, max_delay=0.001)
    stop = MaxAttemptsStopCondition(2)
    retry_always = AsyncRetry(strategy, stop)(always_fail)
    with pytest.raises(RuntimeError):
        await retry_always()
