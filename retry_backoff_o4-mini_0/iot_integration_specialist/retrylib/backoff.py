import random
from .registry import BackoffRegistry

class ExponentialBackoffStrategy:
    def __init__(self, base=1, cap=None):
        self.base = base
        self.cap = cap

    def delay(self, attempt):
        raw = self.base * (2 ** (attempt - 1))
        if self.cap is not None:
            raw = min(raw, self.cap)
        return raw

class FullJitterBackoffStrategy:
    def __init__(self, base=1, cap=None):
        self.base = base
        self.cap = cap

    def delay(self, attempt):
        raw = self.base * (2 ** (attempt - 1))
        if self.cap is not None:
            raw = min(raw, self.cap)
        return random.uniform(0, raw)

# register default strategies
BackoffRegistry.register('exponential', ExponentialBackoffStrategy)
BackoffRegistry.register('full_jitter', FullJitterBackoffStrategy)
