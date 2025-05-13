import asyncio
import pytest
from retry_framework.asyncio_integration import async_retry, AsyncRetryContextManager
from retry_framework.history import RetryHistoryCollector

@pytest.mark.asyncio
async def test_async_retry_decorator():
    @async_retry
    async def hello(name):
        await asyncio.sleep(0)
        return f"hello {name}"
    res = await hello("world")
    assert res == "hello world"

@pytest.mark.asyncio
async def test_async_context_manager_records_history():
    hist = RetryHistoryCollector()
    async with AsyncRetryContextManager(history_collector=hist):
        pass
    entries = hist.get_history()
    assert len(entries) == 2
    assert entries[0]["event"] == "aenter"
    assert entries[1]["event"] == "aexit"
    assert entries[1]["exception"] is None
