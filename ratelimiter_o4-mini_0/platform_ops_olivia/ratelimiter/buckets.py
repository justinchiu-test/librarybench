from .clock import MockableClock

class TokenBucket:
    def __init__(self, capacity, refill_rate, clock=None):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.clock = clock or MockableClock()
        self._tokens = capacity
        self._last = self.clock.now()

    def allow(self):
        now = self.clock.now()
        elapsed = now - self._last
        refill = elapsed * self.refill_rate
        if refill > 0:
            self._tokens = min(self.capacity, self._tokens + refill)
            self._last = now
        if self._tokens >= 1:
            self._tokens -= 1
            return True
        return False

    @property
    def tokens(self):
        return self._tokens

class PriorityBucket(TokenBucket):
    def __init__(self):
        pass

    def allow(self):
        return True
