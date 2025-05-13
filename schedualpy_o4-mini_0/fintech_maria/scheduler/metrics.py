import threading
import time

class MetricsExporter:
    def __init__(self):
        self._counters = {}
        self._histograms = {}
        self._lock = threading.Lock()

    def inc_counter(self, name, amount=1):
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + amount

    def observe_histogram(self, name, value):
        with self._lock:
            self._histograms.setdefault(name, []).append(value)

    def get_counters(self):
        with self._lock:
            return dict(self._counters)

    def get_histograms(self):
        with self._lock:
            return {k: list(v) for k, v in self._histograms.items()}
