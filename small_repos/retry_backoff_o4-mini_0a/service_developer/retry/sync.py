import time
from .backoff import BackoffGeneratorInterface
from .stop import StopConditionInterface
from .history import RetryHistoryCollector
from .context import ContextPropagation
from functools import wraps

class Retry:
    def __init__(self, backoff_strategy, stop_condition, hooks=None, context=None, history_collector=None):
        if not isinstance(backoff_strategy, BackoffGeneratorInterface):
            raise TypeError("backoff_strategy must implement BackoffGeneratorInterface")
        if not isinstance(stop_condition, StopConditionInterface):
            raise TypeError("stop_condition must implement StopConditionInterface")
        self.backoff = backoff_strategy
        self.stop_condition = stop_condition
        self.hooks = hooks or []
        self.context = ContextPropagation(context)
        self.history = history_collector

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while True:
                try:
                    result = func(*args, **kwargs)
                    if self.history:
                        self.history.record(attempt, 0, None, time.time(), True)
                    return result
                except Exception as e:
                    if self.stop_condition.should_stop(attempt):
                        if self.history:
                            self.history.record(attempt, 0, e, time.time(), False)
                        raise
                    delay = self.backoff(attempt)
                    ctx = {'attempt': attempt, 'delay': delay}
                    ctx.update(self.context.get_context())
                    for hook in self.hooks:
                        hook.on_retry(ctx)
                    if self.history:
                        self.history.record(attempt, delay, e, time.time(), False)
                    time.sleep(delay)
                    attempt += 1
        return wrapper

class RetryContextManager:
    def __init__(self, retry_obj):
        self.retry = retry_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def call(self, func, *args, **kwargs):
        decorated = self.retry(func)
        return decorated(*args, **kwargs)
