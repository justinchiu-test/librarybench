import pytest
from ratelimiter.fake import FakeRateLimiter

def test_fake_rate_limiter_allow():
    fr = FakeRateLimiter(always_allow=True)
    assert fr.allow()
    assert fr.requests == 1

def test_fake_rate_limiter_deny():
    fr = FakeRateLimiter(always_allow=False)
    assert not fr.allow()
    assert fr.requests == 1
