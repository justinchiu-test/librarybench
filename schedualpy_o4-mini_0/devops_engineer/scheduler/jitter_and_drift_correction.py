import random

class JitterDriftCorrection:
    def __init__(self, max_jitter_seconds=0):
        self.max_jitter = max_jitter_seconds

    def apply_jitter(self, base_delay):
        if self.max_jitter <= 0:
            return base_delay
        jitter = random.uniform(-self.max_jitter, self.max_jitter)
        return base_delay + jitter
