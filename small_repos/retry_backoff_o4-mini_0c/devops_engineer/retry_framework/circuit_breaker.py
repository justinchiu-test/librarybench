import time
import threading

class CircuitBreakerOpen(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._failure_count = 0
        self._last_failure_time = None
        self._lock = threading.Lock()

    def call(self, func, *args, **kwargs):
        with self._lock:
            if (self._last_failure_time is not None and
                (time.time() - self._last_failure_time) < self.recovery_timeout and
                self._failure_count >= self.failure_threshold):
                raise CircuitBreakerOpen('Circuit is open')
        try:
            result = func(*args, **kwargs)
        except Exception:
            with self._lock:
                self._failure_count += 1
                self._last_failure_time = time.time()
            raise
        else:
            with self._lock:
                self._failure_count = 0
                self._last_failure_time = None
            return result
