class OnRetryHook:
    def __init__(self, callback):
        self.callback = callback

    def __call__(self, attempt_number, exception, delay, context):
        self.callback(attempt_number, exception, delay, context)

class MetricsHook:
    def __init__(self):
        self.attempts = 0
        self.delays = []

    def __call__(self, attempt_number, exception, delay, context):
        self.attempts += 1
        self.delays.append(delay)
