import pytest
from ratelimiter.logger import RateLimitLogger

def test_logger():
    RateLimitLogger.clear()
    RateLimitLogger.log_allow('f', 'c')
    RateLimitLogger.log_throttle('g', 'd')
    assert RateLimitLogger.events == [
        {'func': 'f', 'client': 'c', 'action': 'allow'},
        {'func': 'g', 'client': 'd', 'action': 'throttle'}
    ]
