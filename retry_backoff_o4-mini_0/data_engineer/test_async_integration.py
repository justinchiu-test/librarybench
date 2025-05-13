import pytest
import asyncio
from retry_toolkit.async_integration import async_retry_context

@pytest.mark.asyncio
async def test_async_retry_context_success():
    count = {'c': 0}
    async def work():
        count['c'] += 1
        if count['c'] < 2:
            raise ValueError
    async with async_retry_context(max_attempts=3):
        await work()
    assert count['c'] == 2

@pytest.mark.asyncio
async def test_async_retry_context_fail():
    count = {'c': 0}
    async def work():
        count['c'] += 1
        raise ValueError
    with pytest.raises(ValueError):
        async with async_retry_context(max_attempts=2):
            await work()
    assert count['c'] == 2
