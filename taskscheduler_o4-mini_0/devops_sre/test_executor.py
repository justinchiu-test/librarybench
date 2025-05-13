import pytest
import asyncio
from scheduler.executor import Executor

def square(x):
    return x*x

@pytest.mark.parametrize("mode", ['thread', 'process'])
def test_executor_submit_and_shutdown(mode):
    executor = Executor(mode=mode)
    future = executor.submit(square, 3)
    assert future.result() == 9
    executor.shutdown()

def test_asyncio_executor():
    executor = Executor(mode='asyncio')
    async def add(a, b):
        return a + b
    future = executor.submit(add, 1, 2)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(future)
    assert res == 3
