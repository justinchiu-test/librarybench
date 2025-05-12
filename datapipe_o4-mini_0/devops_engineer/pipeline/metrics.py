import threading

class Metrics:
    def __init__(self):
        self.counters = {}
        self.lock = threading.Lock()

    def increment_counter(self, stage, status):
        with self.lock:
            self.counters.setdefault(stage, {'success': 0, 'failure': 0})
            if status not in self.counters[stage]:
                self.counters[stage][status] = 0
            self.counters[stage][status] += 1

    def get_counts(self, stage):
        with self.lock:
            return dict(self.counters.get(stage, {}))
