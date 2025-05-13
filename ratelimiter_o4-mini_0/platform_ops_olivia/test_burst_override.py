from ratelimiter.buckets import TokenBucket
from ratelimiter.clock import MockableClock
from ratelimiter.overrides import burst_override

def test_burst_override_increases_capacity_temporarily():
    clock = MockableClock(start=0.0)
    bucket = TokenBucket(capacity=2, refill_rate=0, clock=clock)
    assert bucket.allow()
    assert bucket.allow()
    assert not bucket.allow()
    with burst_override(bucket, extra_capacity=3):
        bucket._tokens = bucket.capacity
        for _ in range(5):
            assert bucket.allow()
    bucket._tokens = bucket.capacity
    assert bucket.allow()
    assert bucket.allow()
    assert not bucket.allow()
