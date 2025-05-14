import pytest
import asyncio
from retry_framework.asyncio_integration import async_retry, AsyncRetryContext

count = 0
async def flaky():
    global count
    count += 1
    if count < 2:
        raise ValueError("fail")
    return 'ok'

@pytest.mark.asyncio
async def test_async_retry():
    global count
    count = 0
    func = async_retry(attempts=3)(flaky)
    result = await func()
    assert result == 'ok'

@pytest.mark.asyncio
async def test_async_context():
    async with AsyncRetryContext() as ctx:
        assert hasattr(ctx, 'history')
        ctx.history.record(0,0,None,True)
    assert len(ctx.history.attempts) == 1
