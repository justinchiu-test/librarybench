class RetryHistoryCollector:
    def __init__(self):
        self.attempts = []

    def record(self, attempt, success, time_taken, exception=None):
        self.attempts.append({
            'attempt': attempt,
            'success': success,
            'time_taken': time_taken,
            'exception': exception
        })

    def get_history(self):
        return self.attempts
