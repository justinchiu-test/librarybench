import pytest
import asyncio
from rate_limiter.policies import TokenBucketPolicy
from rate_limiter.async_limiter import async_rate_limiter

@pytest.mark.asyncio
async def test_async_rate_limiter_decorator_allows_and_limits():
    policy = TokenBucketPolicy(rate=1, capacity=1)
    @async_rate_limiter(policy)
    async def foo(x):
        return x + 1

    result = await foo(1)
    assert result == 2
    with pytest.raises(RuntimeError):
        await foo(5)
    await asyncio.sleep(1.1)
    # should allow again
    assert await foo(3) == 4

@pytest.mark.asyncio
async def test_async_rate_limiter_context_manager():
    policy = TokenBucketPolicy(rate=1, capacity=1)
    limiter = async_rate_limiter(policy)
    async with limiter(lambda: None):
        pass
    with pytest.raises(RuntimeError):
        async with limiter(lambda: None):
            pass
