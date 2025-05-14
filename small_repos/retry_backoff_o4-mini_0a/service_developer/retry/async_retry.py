import asyncio
from .backoff import BackoffGeneratorInterface
from .stop import StopConditionInterface
from .history import RetryHistoryCollector
from .context import ContextPropagation
from functools import wraps

class AsyncRetry:
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
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("AsyncRetry can only decorate async functions")
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 1
            while True:
                try:
                    result = await func(*args, **kwargs)
                    if self.history:
                        # note: .time() vs time.sleep() timestamp difference is fine
                        ts = asyncio.get_event_loop().time()
                        self.history.record(attempt, 0, None, ts, True)
                    return result
                except Exception as e:
                    if self.stop_condition.should_stop(attempt):
                        if self.history:
                            ts = asyncio.get_event_loop().time()
                            self.history.record(attempt, 0, e, ts, False)
                        raise
                    delay = self.backoff(attempt)
                    ctx = {'attempt': attempt, 'delay': delay}
                    ctx.update(self.context.get_context())
                    for hook in self.hooks:
                        hook.on_retry(ctx)
                    if self.history:
                        ts = asyncio.get_event_loop().time()
                        self.history.record(attempt, delay, e, ts, False)
                    await asyncio.sleep(delay)
                    attempt += 1
        return wrapper

class AsyncRetryContextManager:
    def __init__(self, retry_obj):
        self.retry = retry_obj

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def call(self, func, *args, **kwargs):
        decorated = self.retry(func)
        return await decorated(*args, **kwargs)
