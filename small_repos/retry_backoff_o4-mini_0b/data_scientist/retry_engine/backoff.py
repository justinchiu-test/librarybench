import random
from .backoff_registry import BackoffRegistry

class ExponentialBackoffStrategy:
    def __init__(self, base=1.0, max_delay=None):
        self.base = base
        self.max_delay = max_delay

    def next_delay(self, attempt):
        delay = self.base * (2 ** (attempt - 1))
        if self.max_delay is not None:
            delay = min(delay, self.max_delay)
        return delay

BackoffRegistry.register('exponential')(ExponentialBackoffStrategy)

class FullJitterBackoffStrategy:
    def __init__(self, base=1.0, max_delay=None):
        self.base = base
        self.max_delay = max_delay

    def next_delay(self, attempt):
        cap = self.base * (2 ** (attempt - 1))
        if self.max_delay is not None:
            cap = min(cap, self.max_delay)
        return random.uniform(0, cap)

BackoffRegistry.register('full_jitter')(FullJitterBackoffStrategy)
