import pytest
from ratelimiter.buckets import TokenBucket
from ratelimiter.async_limiter import async_rate_limiter, RateLimitExceeded
from ratelimiter.clock import MockableClock

@pytest.mark.asyncio
async def test_async_rate_limiter_allows_and_blocks():
    clock = MockableClock(start=0.0)
    bucket = TokenBucket(capacity=1, refill_rate=0, clock=clock)
    @async_rate_limiter(bucket)
    async def handler(x):
        return x * 2

    result = await handler(3)
    assert result == 6
    with pytest.raises(RateLimitExceeded):
        await handler(1)
