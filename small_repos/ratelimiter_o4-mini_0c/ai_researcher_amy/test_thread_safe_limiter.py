from ratelimiter.token_bucket import TokenBucket
from ratelimiter.thread_safe import ThreadSafeLimiter

def test_thread_safe_limiter():
    tb = TokenBucket(10, 10)
    tsl = ThreadSafeLimiter(tb)
    assert tsl.allow()
    for _ in range(9):
        assert tsl.allow()
    assert not tsl.allow()
