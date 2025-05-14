from abc import ABC, abstractmethod

class RetryHook(ABC):
    @abstractmethod
    def on_retry(self, attempt: int, exception: Exception, delay: float, context: dict):
        pass

class RetryHistoryCollector(RetryHook):
    def __init__(self):
        self.history = []

    def on_retry(self, attempt, exception, delay, context):
        self.history.append({
            'attempt': attempt,
            'exception': exception,
            'delay': delay,
            'context': context.copy()
        })

class MetricsHook(RetryHook):
    def __init__(self):
        self.attempts = 0

    def on_retry(self, attempt, exception, delay, context):
        self.attempts += 1

class StatsDHook(RetryHook):
    def __init__(self, client, metric_name):
        self.client = client
        self.metric_name = metric_name

    def on_retry(self, attempt, exception, delay, context):
        self.client.increment(self.metric_name)

class PrometheusHook(RetryHook):
    def __init__(self, counter, labelnames=None, labelvalues=None):
        self.counter = counter
        self.labelnames = labelnames or []
        self.labelvalues = labelvalues or []

    def on_retry(self, attempt, exception, delay, context):
        self.counter.inc()
