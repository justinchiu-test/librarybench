from ratelimiter.token_bucket import TokenBucket
from ratelimiter.utils import inspect_limiter, burst_override

def test_inspect_limiter():
    tb = TokenBucket(2, 3)
    state = inspect_limiter(tb)
    assert state['refill_rate'] == 2
    assert state['capacity'] == 3

def test_burst_override():
    tb = TokenBucket(1, 1)
    tb._tokens = 0
    assert not tb.allow()
    with burst_override(tb, extra_capacity=5):
        tb._tokens = 0
        assert tb.capacity == 6
        for _ in range(6):
            assert tb.allow()
    assert tb.capacity == 1
