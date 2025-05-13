import threading

class ThreadSafeLimiter:
    def __init__(self, limiter):
        self._limiter = limiter
        self._lock = threading.Lock()

    def allow(self, *args, **kwargs):
        with self._lock:
            return self._limiter.allow(*args, **kwargs)
