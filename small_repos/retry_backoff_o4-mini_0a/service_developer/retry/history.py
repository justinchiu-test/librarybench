class RetryHistoryCollector:
    def __init__(self):
        self.history = []

    def record(self, attempt, delay, exception, timestamp, success):
        self.history.append({
            'attempt': attempt,
            'delay': delay,
            'exception': exception,
            'timestamp': timestamp,
            'success': success,
        })
