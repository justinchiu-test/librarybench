import time

class CircuitOpenException(Exception):
    pass

class CircuitBreakerIntegration:
    def __init__(self, failure_threshold=3, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.opened_at = None

    def before_call(self):
        if self.opened_at is not None:
            if time.time() - self.opened_at >= self.recovery_timeout:
                self.reset()
            else:
                raise CircuitOpenException("Circuit is open")

    def after_call(self, success):
        if success:
            self.reset()
        else:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.opened_at = time.time()

    def reset(self):
        self.failure_count = 0
        self.opened_at = None
