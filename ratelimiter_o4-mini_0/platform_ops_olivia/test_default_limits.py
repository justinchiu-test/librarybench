from ratelimiter.limits import default_limits
from ratelimiter.buckets import TokenBucket

@default_limits
def dummy():
    return True

def test_default_limits_decorator_attaches_limiter():
    assert hasattr(dummy, '_limiter')
    limiter = dummy._limiter
    assert isinstance(limiter, TokenBucket)
    for _ in range(5):
        assert limiter.allow()
    assert not limiter.allow()
