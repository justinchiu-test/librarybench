import threading

class ThreadSafeLimiter:
    def __init__(self, limiter):
        self.limiter = limiter
        self._lock = threading.Lock()

    def allow(self):
        with self._lock:
            return self.limiter.allow()

    async def allow_async(self):
        with self._lock:
            return self.limiter.allow()
