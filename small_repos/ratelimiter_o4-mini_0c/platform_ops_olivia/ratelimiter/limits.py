from .buckets import TokenBucket

def default_limits(func):
    limiter = TokenBucket(capacity=5, refill_rate=1)
    func._limiter = limiter
    return func
