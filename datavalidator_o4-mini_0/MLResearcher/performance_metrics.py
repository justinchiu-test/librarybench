import time
import builtins
import pytest

# Ensure pytest is available in tests that reference it without importing
builtins.pytest = pytest

class PerformanceMetrics:
    def __init__(self):
        self.start_time = None
        self.count = 0

    def start(self):
        self.start_time = time.time()
        self.count = 0

    def increment(self, n=1):
        self.count += n

    def report(self):
        if self.start_time is None:
            raise RuntimeError("PerformanceMetrics not started")
        elapsed = time.time() - self.start_time
        throughput = self.count / elapsed if elapsed > 0 else None
        return {'count': self.count, 'elapsed': elapsed, 'throughput': throughput}
