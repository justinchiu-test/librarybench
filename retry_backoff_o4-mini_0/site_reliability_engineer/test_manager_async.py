import pytest
import asyncio
from retry.backoff import ExponentialBackoffStrategy
from retry.stop_condition import MaxAttemptsStopCondition
from retry.manager import RetryManager
from retry.hooks import MetricsHook, RetryHistoryCollector

@pytest.mark.asyncio
async def test_retry_manager_async_success():
    attempts = []
    async def flaky():
        attempts.append(1)
        if len(attempts) < 2:
            raise ValueError("err")
        return "done"

    backoff = ExponentialBackoffStrategy(base=0)
    stop = MaxAttemptsStopCondition(max_attempts=3)
    metrics = MetricsHook()
    history = RetryHistoryCollector()
    mgr = RetryManager(
        backoff, stop,
        hooks=[metrics, history],
        context={'a': 1},
        async_sleep_func=lambda x: asyncio.sleep(0)
    )
    async with AsyncCtx(mgr) as m:
        result = await m.call_async(flaky)
    assert result == "done"
    assert metrics.retry_count == 1
    assert history.history[0]['event'] == 'retry'
    assert history.history[1]['event'] == 'success'

class AsyncCtx:
    def __init__(self, mgr):
        self.mgr = mgr
    async def __aenter__(self):
        for hook in self.mgr.hooks:
            if hasattr(hook, 'on_start'):
                hook.on_start()
        return self.mgr
    async def __aexit__(self, exc_type, exc, tb):
        return False
