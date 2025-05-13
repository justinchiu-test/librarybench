import pytest
from ratelimiter.clock import MockableClock

def test_clock_now_and_advance():
    clock = MockableClock(start=1000.0)
    assert clock.now() == 1000.0
    clock.advance(5.5)
    assert clock.now() == 1005.5
