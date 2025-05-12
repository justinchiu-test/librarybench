from threading import Lock

class CounterManager:
    def __init__(self):
        self._counters = {'ticks': 0, 'successes': 0, 'failures': 0}
        self._lock = Lock()

    def increment(self, counter_name):
        with self._lock:
            if counter_name in self._counters:
                self._counters[counter_name] += 1
            else:
                raise KeyError(f"Counter '{counter_name}' not found")

    def get(self, counter_name):
        with self._lock:
            if counter_name in self._counters:
                return self._counters[counter_name]
            else:
                raise KeyError(f"Counter '{counter_name}' not found")

    def get_all(self):
        with self._lock:
            return dict(self._counters)
