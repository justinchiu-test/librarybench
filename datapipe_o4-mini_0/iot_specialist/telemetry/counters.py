import threading
from collections import defaultdict

class CounterManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.counters = defaultdict(int)
        self.parsed = defaultdict(int)
        self.dropped = defaultdict(int)

    def increment_counter(self, device_type, parsed=True):
        with self.lock:
            self.counters[device_type] += 1
            if parsed:
                self.parsed[device_type] += 1
            else:
                self.dropped[device_type] += 1

    def get_counts(self, device_type):
        with self.lock:
            return {
                'total': self.counters.get(device_type, 0),
                'parsed': self.parsed.get(device_type, 0),
                'dropped': self.dropped.get(device_type, 0)
            }

counter_manager = CounterManager()
