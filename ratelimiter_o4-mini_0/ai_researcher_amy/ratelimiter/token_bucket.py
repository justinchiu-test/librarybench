import threading
import time

class TokenBucket:
    def __init__(self, refill_rate, bucket_capacity, clock=None):
        self.refill_rate = refill_rate
        self.capacity = bucket_capacity
        self._tokens = bucket_capacity
        self._clock = clock if clock is not None else time
        if hasattr(self._clock, 'now'):
            self._last = self._clock.now()
        else:
            self._last = time.monotonic()
        self._lock = threading.Lock()

    def allow(self, tokens=1):
        with self._lock:
            if hasattr(self._clock, 'now'):
                now = self._clock.now()
            else:
                now = time.monotonic()
            elapsed = now - self._last
            refill = elapsed * self.refill_rate
            self._tokens = min(self.capacity, self._tokens + refill)
            self._last = now
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False
