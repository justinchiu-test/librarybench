import pytest
import time
from file_watcher.core import Throttler, Event

def test_throttler_allows_when_rate_zero():
    t = Throttler(rate=0)
    ev = Event('p', 't')
    for _ in range(5):
        assert t.allow(ev)

def test_throttler_limits_rate():
    t = Throttler(rate=2)
    e = Event('p', 't')
    assert t.allow(e)
    assert t.allow(e)
    # third within same second should be blocked
    assert not t.allow(e)
    # after waiting, allowed again
    time.sleep(1.1)
    assert t.allow(e)
