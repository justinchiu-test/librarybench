import time

class CircuitOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'CLOSED'

    def call(self, fn, *args, **kwargs):
        now = time.time()
        if self.state == 'OPEN':
            if now - self.last_failure_time >= self.recovery_timeout:
                self.state = 'HALF_OPEN'
            else:
                raise CircuitOpenException("Circuit is open")
        try:
            result = fn(*args, **kwargs)
        except Exception as e:
            self._record_failure(now)
            raise
        else:
            self._reset()
            return result

    def _record_failure(self, now):
        self.failures += 1
        self.last_failure_time = now
        if self.failures >= self.failure_threshold:
            self.state = 'OPEN'

    def _reset(self):
        self.failures = 0
        self.last_failure_time = None
        self.state = 'CLOSED'
