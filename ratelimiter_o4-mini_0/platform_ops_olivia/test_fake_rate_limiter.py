import pytest
from ratelimiter.fixtures import FakeRateLimiter

def test_fake_rate_limiter_allows_up_to_capacity():
    limiter = FakeRateLimiter(capacity=2)
    assert limiter.allow()
    assert limiter.allow()
    assert not limiter.allow()
