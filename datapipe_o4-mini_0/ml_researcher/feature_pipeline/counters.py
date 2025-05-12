import threading

class IncrementCounter:
    def __init__(self):
        self._lock = threading.Lock()
        self._counts = {}

    def increment(self, name, value=1):
        with self._lock:
            self._counts[name] = self._counts.get(name, 0) + value

    def get(self, name):
        with self._lock:
            return self._counts.get(name, 0)

# module-level counter
counter = IncrementCounter()
