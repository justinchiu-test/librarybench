import time

class MonitoringMetrics:
    def __init__(self):
        self.counters = {}
        self.timings = {}
    def inc(self, key, amount=1):
        self.counters[key] = self.counters.get(key, 0) + amount
    def record_time(self, sample, duration):
        self.timings.setdefault(sample, []).append(duration)
    def get_counters(self):
        return dict(self.counters)
    def get_timings(self):
        return {k: list(v) for k, v in self.timings.items()}
    def snapshot(self):
        return {'counters': self.get_counters(), 'timings': self.get_timings()}
