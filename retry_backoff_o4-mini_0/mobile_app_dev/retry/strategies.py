import os
import random

class ExponentialBackoffStrategy:
    def __init__(self, initial_delay=1, max_delay=60):
        self.initial_delay = float(os.getenv('EXPONENTIAL_INITIAL_DELAY', initial_delay))
        self.max_delay = float(os.getenv('EXPONENTIAL_MAX_DELAY', max_delay))

    def delay(self, attempt):
        delay = self.initial_delay * (2 ** (attempt - 1))
        return min(delay, self.max_delay)

class FullJitterBackoffStrategy:
    def __init__(self, initial_delay=1, max_delay=60):
        self.initial_delay = float(os.getenv('JITTER_INITIAL_DELAY', initial_delay))
        self.max_delay = float(os.getenv('JITTER_MAX_DELAY', max_delay))

    def delay(self, attempt):
        cap = min(self.initial_delay * (2 ** (attempt - 1)), self.max_delay)
        return random.uniform(0, cap)
