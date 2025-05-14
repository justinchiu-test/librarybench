import pytest
from ratelimiter.token_bucket import TokenBucket
from ratelimiter.decorators import default_limits, whitelist_client
from ratelimiter.logger import RateLimitLogger

def test_default_limits_allow_and_throttle():
    RateLimitLogger.clear()
    tb = TokenBucket(1, 1)
    @default_limits(tb)
    def f(x, client=None):
        return x
    assert f(10) == 10
    with pytest.raises(Exception):
        f(20)
    events = RateLimitLogger.events
    assert events[0]['action'] == 'allow'
    assert events[1]['action'] == 'throttle'

def test_whitelist_client_bypass():
    RateLimitLogger.clear()
    tb = TokenBucket(1, 1)
    @whitelist_client(['special'])
    @default_limits(tb)
    def f(x, client=None):
        return x
    # non-special client: enforce limit
    assert f(1, client='normal') == 1
    with pytest.raises(Exception):
        f(2, client='normal')
    # special client: bypass limit
    result = f(100, client='special')
    assert result == 100
