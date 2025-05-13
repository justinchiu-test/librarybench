import asyncio
import functools
import time
from .backoff import BackoffRegistry
from .history import RetryHistoryCollector

def async_retry(attempts=3, backoff='exponential'):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            strategy = BackoffRegistry.get(backoff)
            hist = RetryHistoryCollector()
            last_exception = None
            for attempt in range(1, attempts + 1):
                delay = strategy(attempt)
                try:
                    result = await func(*args, **kwargs)
                    hist.record(time.time(), delay, None, True)
                    return result
                except Exception as e:
                    hist.record(time.time(), delay, e, False)
                    last_exception = e
                    await asyncio.sleep(delay)
            if last_exception:
                raise last_exception
        return wrapper
    return decorator

class AsyncRetryContext:
    def __init__(self):
        self.history = RetryHistoryCollector()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False
