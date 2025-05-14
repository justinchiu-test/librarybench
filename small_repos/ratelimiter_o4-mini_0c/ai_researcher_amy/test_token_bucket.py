import pytest
from ratelimiter.token_bucket import TokenBucket
from ratelimiter.clock import MockableClock

def test_token_bucket_initial():
    tb = TokenBucket(1, 5)
    for _ in range(5):
        assert tb.allow()
    assert not tb.allow()

def test_token_bucket_refill():
    clock = MockableClock()
    tb = TokenBucket(refill_rate=1, bucket_capacity=5, clock=clock)
    for _ in range(5):
        assert tb.allow()
    assert not tb.allow()
    clock.advance(3)
    assert tb.allow()
