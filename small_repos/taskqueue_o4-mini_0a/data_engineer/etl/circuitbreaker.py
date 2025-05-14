import time

class CircuitOpenError(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold=3, reset_timeout=60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = {}
        self.opened_at = {}

    def record_success(self, name):
        self.failures.pop(name, None)
        self.opened_at.pop(name, None)

    def record_failure(self, name):
        cnt = self.failures.get(name, 0) + 1
        self.failures[name] = cnt
        if cnt >= self.failure_threshold:
            self.opened_at[name] = time.time()

    def can_retry(self, name):
        if name not in self.opened_at:
            return True
        opened = self.opened_at[name]
        if time.time() - opened >= self.reset_timeout:
            # reset
            self.record_success(name)
            return True
        return False
