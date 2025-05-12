import threading

_counters = {}
_lock = threading.Lock()

class Counter:
    def __init__(self, name):
        self.name = name
        self._value = 0
        self._lock = threading.Lock()

    def inc(self, amount=1):
        with self._lock:
            self._value += amount

    def get_count(self):
        with self._lock:
            return self._value

def create_counter(name):
    with _lock:
        if name not in _counters:
            _counters[name] = Counter(name)
        return _counters[name]

def monitor_pipeline():
    for name, counter in _counters.items():
        print(f"Counter {name}: {counter.get_count()}")
