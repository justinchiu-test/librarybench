from ratelimiter.buckets import TokenBucket
from ratelimiter.clock import MockableClock
from ratelimiter.inspect import inspect_limiter

def test_inspect_limiter_reports_state():
    clock = MockableClock(start=0.0)
    bucket = TokenBucket(capacity=3, refill_rate=1, clock=clock)
    assert bucket.allow()
    state = inspect_limiter(bucket)
    assert state['capacity'] == 3
    assert 'tokens' in state
    assert state['tokens'] == bucket.tokens
