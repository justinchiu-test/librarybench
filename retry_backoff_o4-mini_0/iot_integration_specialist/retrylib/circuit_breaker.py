import time

class CircuitOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold, recovery_timeout):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = 'closed'  # 'closed', 'open', 'half_open'
        self.last_failure_time = None

    def before_call(self):
        if self.state == 'open':
            now = time.time()
            if self.last_failure_time is not None and (now - self.last_failure_time) < self.recovery_timeout:
                raise CircuitOpenException("Circuit is open")
            else:
                self.state = 'half_open'

    def after_call(self, success):
        if success:
            self.failure_count = 0
            self.state = 'closed'
            self.last_failure_time = None
        else:
            self.failure_count += 1
            if self.state == 'half_open' or self.failure_count >= self.failure_threshold:
                self.state = 'open'
                self.last_failure_time = time.time()
