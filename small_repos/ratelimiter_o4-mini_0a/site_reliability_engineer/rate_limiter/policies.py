import time
from .logging import log_event

class TokenBucketPolicy:
    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.timestamp = time.time()
    def allow(self, key=None):
        now = time.time()
        elapsed = now - self.timestamp
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.timestamp = now
        if self.tokens >= 1:
            self.tokens -= 1
            log_event("token_bucket", "allow", {"tokens_left": self.tokens})
            return True
        else:
            log_event("token_bucket", "throttle", {"tokens": self.tokens})
            return False
    def get_metrics(self):
        next_refill = (1 - self.tokens) / self.rate if self.rate > 0 else None
        return {"tokens": self.tokens, "capacity": self.capacity, "next_refill": next_refill}

class FixedWindowPolicy:
    def __init__(self, limit, window_seconds):
        self.limit = limit
        self.window = window_seconds
        self.count = 0
        self.start = time.time()
    def allow(self, key=None):
        now = time.time()
        if now - self.start >= self.window:
            self.start = now
            self.count = 0
        if self.count < self.limit:
            self.count += 1
            log_event("fixed_window", "allow", {"count": self.count})
            return True
        else:
            log_event("fixed_window", "throttle", {"count": self.count})
            return False
    def get_metrics(self):
        time_left = self.window - (time.time() - self.start)
        return {"count": self.count, "limit": self.limit, "time_left": time_left}

def chain_policies(policies, mode="series"):
    def checker(key=None):
        if mode == "series":
            for p in policies:
                if not p.allow(key):
                    return False
            return True
        elif mode == "parallel":
            for p in policies:
                if p.allow(key):
                    return True
            return False
        else:
            raise ValueError("Unknown mode")
    return checker
