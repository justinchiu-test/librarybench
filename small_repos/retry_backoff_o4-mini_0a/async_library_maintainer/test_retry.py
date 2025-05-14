import pytest
import asyncio

from retry_lib.context import get_context, set_context, clear_context
from retry_lib.core import Retry

@pytest.mark.anyio
async def test_async_retry_decorator_and_context():
    calls = {'count': 0}

    async def flaky_async():
        calls['count'] += 1
        if get_context('trace_id') != 'abc':
            raise RuntimeError("no trace")
        if calls['count'] < 2:
            raise RuntimeError("fail")
        return "async ok"

    set_context('trace_id', 'abc')
    retry = Retry()
    decorated = retry(flaky_async)
    result = await decorated()
    assert result == "async ok"
    clear_context()

def test_context_in_async_tasks():
    async def worker():
        return get_context('a')

    async def main():
        set_context('a', 'val')
        task = asyncio.create_task(worker())
        return await task

    res = asyncio.get_event_loop().run_until_complete(main())
    assert res == 'val'
    clear_context()
