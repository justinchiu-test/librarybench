import pytest
from ratelimiter.clock import MockableClock

def test_mockable_clock():
    mc = MockableClock()
    t1 = mc.now()
    mc.advance(5)
    t2 = mc.now()
    assert abs((t2 - t1) - 5) < 1e-6
