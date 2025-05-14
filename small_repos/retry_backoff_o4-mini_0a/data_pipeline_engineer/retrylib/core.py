import time
from .backoff import BackoffGeneratorInterface
from .history import RetryHistoryCollector

class Retry:
    def __init__(self, backoff_strategy, stop_condition, hooks=None, context=None, history_collector=None):
        if not isinstance(backoff_strategy, BackoffGeneratorInterface):
            raise ValueError("backoff_strategy must implement BackoffGeneratorInterface")
        self.backoff_strategy = backoff_strategy
        self.stop_condition = stop_condition
        self.hooks = hooks or []
        self.context = context
        self.history = history_collector

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                attempt += 1
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    timestamp = time.time()
                    delay = self.backoff_strategy.next_backoff()
                    for hook in self.hooks:
                        hook(attempt, e, delay, self.context)
                    if self.history:
                        self.history.record(attempt, delay, e, timestamp, self.context)
                    if self.stop_condition and self.stop_condition.should_stop(attempt):
                        raise
                    time.sleep(delay)
        return wrapper
