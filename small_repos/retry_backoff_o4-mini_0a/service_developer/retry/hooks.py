from abc import ABC, abstractmethod

class OnRetryHookInterface(ABC):
    @abstractmethod
    def on_retry(self, context: dict):
        pass

class MetricsHook(OnRetryHookInterface):
    def __init__(self):
        self.retry_count = 0
        self.latencies = []

    def on_retry(self, context: dict):
        self.retry_count += 1
        self.latencies.append(context.get('delay'))
