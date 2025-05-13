import threading

class RetryHistoryCollector:
    def __init__(self):
        self.lock = threading.Lock()
        self.attempts = []

    def record(self, timestamp, delay, exception, outcome):
        with self.lock:
            self.attempts.append({
                'timestamp': timestamp,
                'delay': delay,
                'exception': exception,
                'outcome': outcome
            })
