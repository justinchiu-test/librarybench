import threading
from scheduler.concurrency import ConcurrencyLimiter

def test_limiter_blocks_and_releases():
    limiter = ConcurrencyLimiter(2)
    # acquire twice
    limiter.acquire()
    limiter.acquire()
    # semaphore count should be zero
    assert limiter._sem._value == 0
    # release once
    limiter.release()
    assert limiter._sem._value == 1
    # context manager
    with limiter:
        # inside, value should decrease
        assert limiter._sem._value == 0
    # after exit, back to 1
    assert limiter._sem._value == 1
