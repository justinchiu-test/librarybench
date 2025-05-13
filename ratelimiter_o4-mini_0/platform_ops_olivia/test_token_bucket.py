from ratelimiter.buckets import TokenBucket
from ratelimiter.clock import MockableClock

def test_token_bucket_refills_and_enforces_capacity():
    clock = MockableClock(start=0.0)
    bucket = TokenBucket(capacity=2, refill_rate=1, clock=clock)
    assert bucket.allow()
    assert bucket.allow()
    assert not bucket.allow()
    clock.advance(1.0)
    assert bucket.allow()
    assert not bucket.allow()
    clock.advance(2.0)
    assert bucket.allow()
    assert bucket.allow()
    assert not bucket.allow()
