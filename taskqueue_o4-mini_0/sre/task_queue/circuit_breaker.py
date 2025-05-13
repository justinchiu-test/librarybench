import time

class CircuitOpen(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=60):
        # service -> failure count
        self.failures = {}
        # service -> circuit open until timestamp
        self.open_until = {}
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

    def allow_request(self, service):
        until = self.open_until.get(service, 0)
        now = time.time()
        if now < until:
            return False
        return True

    def record_failure(self, service):
        count = self.failures.get(service, 0) + 1
        self.failures[service] = count
        if count >= self.failure_threshold:
            # open circuit
            self.open_until[service] = time.time() + self.recovery_timeout
            self.failures[service] = 0

    def record_success(self, service):
        # reset failures on success
        self.failures[service] = 0
        self.open_until[service] = 0
