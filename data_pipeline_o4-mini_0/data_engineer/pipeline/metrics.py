import time
import threading

class MonitoringMetrics:
    def __init__(self):
        self.counters = {}
        self.gauges = {}
        self.timers = {}
        self._lock = threading.Lock()

    def inc_counter(self, name, amount=1):
        with self._lock:
            self.counters[name] = self.counters.get(name, 0) + amount

    def set_gauge(self, name, value):
        with self._lock:
            self.gauges[name] = value

    def time_context(self, name):
        return _TimerContext(self, name)

class _TimerContext:
    def __init__(self, metrics, name):
        self.metrics = metrics
        self.name = name

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start
        with self.metrics._lock:
            self.metrics.timers.setdefault(self.name, []).append(elapsed)
