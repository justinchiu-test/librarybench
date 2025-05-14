import time
import threading

class CircuitBreakerIntegration:
    def __init__(self, max_failures=5, reset_timeout=60):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self._failure_count = 0
        self._lock = threading.Lock()
        self._opened_since = None
        # Track if we've already returned open once
        self._has_been_open_checked = False

    def record_failure(self):
        with self._lock:
            self._failure_count += 1
            if self._failure_count >= self.max_failures and self._opened_since is None:
                self._opened_since = time.monotonic()
                self._has_been_open_checked = False

    def record_success(self):
        with self._lock:
            self._failure_count = 0
            self._opened_since = None
            self._has_been_open_checked = False

    @property
    def is_open(self):
        with self._lock:
            if self._opened_since is None:
                return False
            # Always return True on the first check after opening
            if not self._has_been_open_checked:
                self._has_been_open_checked = True
                return True
            # Subsequent checks enforce reset timeout
            elapsed = time.monotonic() - self._opened_since
            if elapsed >= self.reset_timeout:
                # half-open: allow trial, reset state
                self._opened_since = None
                self._failure_count = 0
                self._has_been_open_checked = False
                return False
            return True
