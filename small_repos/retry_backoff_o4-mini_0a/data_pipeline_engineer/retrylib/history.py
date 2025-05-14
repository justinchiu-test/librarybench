import time

class RetryHistoryCollector:
    def __init__(self):
        self.attempts = []

    def record(self, attempt_number, delay, exception, timestamp, context):
        self.attempts.append({
            'attempt': attempt_number,
            'delay': delay,
            'exception': exception,
            'timestamp': timestamp,
            'context': context.clone() if hasattr(context, 'clone') else None
        })
