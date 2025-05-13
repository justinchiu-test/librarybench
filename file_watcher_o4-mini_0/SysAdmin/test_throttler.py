import time
from audit_watcher.throttler import Throttler

def test_throttler_limit():
    thr = Throttler(limit_per_second=2)
    assert thr.allow()
    assert thr.allow()
    assert not thr.allow()
    time.sleep(1.1)
    assert thr.allow()
