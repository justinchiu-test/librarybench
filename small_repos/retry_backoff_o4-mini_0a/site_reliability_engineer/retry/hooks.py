import time

class OnRetryHook:
    def __init__(self, callback):
        self.callback = callback

    def on_retry(self, attempt, exception, delay, context):
        self.callback(attempt, exception, delay, context)

class MetricsHook:
    def __init__(self):
        self.retry_count = 0
        self.failure_count = 0
        self.success = False
        self.latency = None
        self._start = None

    def on_start(self):
        self._start = time.time()

    def on_retry(self, attempt, exception, delay, context):
        self.retry_count += 1

    def on_success(self, attempt, result, context):
        self.success = True
        if self._start is not None:
            self.latency = time.time() - self._start

    def on_failure(self, attempt, exception, context):
        self.failure_count += 1
        if self._start is not None:
            self.latency = time.time() - self._start

class RetryHistoryCollector:
    def __init__(self):
        self.history = []

    def on_retry(self, attempt, exception, delay, context):
        entry = {
            'event': 'retry',
            'attempt': attempt,
            'exception': exception,
            'delay': delay,
            'context': context.copy() if isinstance(context, dict) else context
        }
        self.history.append(entry)

    def on_success(self, attempt, result, context):
        entry = {
            'event': 'success',
            'attempt': attempt,
            'result': result,
            'context': context.copy() if isinstance(context, dict) else context
        }
        self.history.append(entry)

    def on_failure(self, attempt, exception, context):
        entry = {
            'event': 'failure',
            'attempt': attempt,
            'exception': exception,
            'context': context.copy() if isinstance(context, dict) else context
        }
        self.history.append(entry)
