import threading

class ExecutionContext:
    """Thread-safe context for sharing data among tasks."""
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()

    def set(self, key, value):
        """Set a value in the context."""
        with self._lock:
            self._data[key] = value

    def get(self, key, default=None):
        """Get a value from the context."""
        with self._lock:
            return self._data.get(key, default)
