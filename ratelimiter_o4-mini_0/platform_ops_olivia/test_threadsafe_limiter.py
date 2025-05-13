import threading
from ratelimiter.threadsafe import ThreadSafeLimiter
from ratelimiter.fixtures import FakeRateLimiter

def test_threadsafe_limiter_with_multiple_threads():
    base = FakeRateLimiter(capacity=1)
    limiter = ThreadSafeLimiter(base)
    results = []

    def worker():
        results.append(limiter.allow())

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert results.count(True) == 1
    assert results.count(False) == 4
