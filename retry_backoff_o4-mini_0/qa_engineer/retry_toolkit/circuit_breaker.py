import time
import threading

class CircuitBreaker:
    def __init__(self, failure_threshold=3, reset_timeout=5):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self._failure_count = 0
        self._state = "CLOSED"
        self._opened_time = None
        self._lock = threading.Lock()

    @property
    def is_open(self):
        with self._lock:
            # If circuit is open and timeout has passed, reset it
            if self._state == "OPEN":
                if (time.time() - self._opened_time) >= self.reset_timeout:
                    self._state = "CLOSED"
                    self._failure_count = 0
            return self._state == "OPEN"

    def call(self, func, *args, **kwargs):
        # Check open state without holding the lock to avoid deadlock
        if self.is_open:
            raise Exception("Circuit is open")
        try:
            result = func(*args, **kwargs)
        except Exception:
            # On failure, increment count and open if threshold reached
            with self._lock:
                self._failure_count += 1
                if self._failure_count >= self.failure_threshold:
                    self._state = "OPEN"
                    self._opened_time = time.time()
            # Propagate the original exception
            raise
        else:
            # On success, reset failure count
            with self._lock:
                self._failure_count = 0
            return result

    def reset(self):
        with self._lock:
            self._state = "CLOSED"
            self._failure_count = 0
            self._opened_time = None
