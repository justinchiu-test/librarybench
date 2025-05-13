import time
from contextlib import contextmanager

class MonitoringMetrics:
    def __init__(self):
        self.counters = {}
        self.gauges = {}
        self.timers = {}

    def inc_counter(self, name, value=1):
        self.counters[name] = self.counters.get(name, 0) + value

    def set_gauge(self, name, value):
        self.gauges[name] = value

    @contextmanager
    def timer(self, name):
        start = time.time()
        yield
        elapsed = time.time() - start
        self.timers[name] = elapsed
