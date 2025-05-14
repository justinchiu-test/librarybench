import pytest
from ratelimiter.token_bucket import TokenBucket
from ratelimiter.decorators import async_rate_limiter
from ratelimiter.logger import RateLimitLogger

@pytest.mark.asyncio
async def test_async_rate_limiter():
    RateLimitLogger.clear()
    tb = TokenBucket(1, 1)
    @async_rate_limiter(tb)
    async def f(x):
        return x
    assert await f(5) == 5
    with pytest.raises(Exception):
        await f(6)
    actions = [e['action'] for e in RateLimitLogger.events]
    assert actions == ['allow', 'throttle']
