import time

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreakerIntegration:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'

    def before_call(self):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerOpenException("Circuit is open")

    def after_call(self, success):
        if success:
            self.failure_count = 0
            self.state = 'CLOSED'
        else:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
