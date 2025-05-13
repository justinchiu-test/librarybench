import pytest
import asyncio
from retry.backoff import ExponentialBackoffStrategy
from retry.stop import MaxAttemptsStopCondition
from retry.hooks import MetricsHook
from retry.history import RetryHistoryCollector
# Changed import to point at async_retry.py instead of a reserved word module name
from retry.async_retry import AsyncRetry

@pytest.mark.asyncio
async def test_async_retry_success():
    counter = {'count': 0}
    async def async_flaky():
        counter['count'] += 1
        if counter['count'] < 3:
            raise ValueError("fail")
        return "ok"
    backoff = ExponentialBackoffStrategy(base=0)
    stop = MaxAttemptsStopCondition(5)
    metrics = MetricsHook()
    history = RetryHistoryCollector()
    retry = AsyncRetry(backoff, stop, hooks=[metrics], history_collector=history)
    func = retry(async_flaky)
    result = await func()
    assert result == "ok"
    assert metrics.retry_count == 2
    assert history.history[-1]['success'] is True

@pytest.mark.asyncio
async def test_async_retry_exhausts():
    backoff = ExponentialBackoffStrategy(base=0)
    stop = MaxAttemptsStopCondition(2)
    history = RetryHistoryCollector()
    retry = AsyncRetry(backoff, stop, history_collector=history)
    @retry
    async def always_fail():
        raise RuntimeError("err")
    with pytest.raises(RuntimeError):
        await always_fail()
    assert len(history.history) == 2
