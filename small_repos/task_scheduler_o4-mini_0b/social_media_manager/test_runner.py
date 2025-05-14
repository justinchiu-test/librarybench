import pytest
import asyncio
from postscheduler.runner import run_coroutine

@pytest.mark.asyncio
async def test_run_coroutine_success():
    async def coro1():
        await asyncio.sleep(0.01)
        return 1
    async def coro2():
        return 2
    results = await run_coroutine([coro1(), coro2()])
    assert results == [1, 2]
