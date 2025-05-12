import threading
from . import config

class Counter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def inc(self, amount=1):
        with self._lock:
            self._value += amount

    def get(self):
        with self._lock:
            return self._value

def create_counter(name):
    counter = Counter()
    config.counters[name] = counter
    return counter
