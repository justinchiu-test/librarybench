import threading

class CircuitOpen(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold=3):
        self.failure_threshold = failure_threshold
        self._failure_count = 0
        self._open = False
        self._lock = threading.Lock()

    def call(self, func, *args, **kwargs):
        with self._lock:
            if self._open:
                raise CircuitOpen("Circuit is open; calls are blocked")
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            with self._lock:
                self._failure_count += 1
                if self._failure_count >= self.failure_threshold:
                    self._open = True
            raise
        else:
            with self._lock:
                self._failure_count = 0
            return result

    def is_open(self):
        with self._lock:
            return self._open

    def reset(self):
        with self._lock:
            self._failure_count = 0
            self._open = False
