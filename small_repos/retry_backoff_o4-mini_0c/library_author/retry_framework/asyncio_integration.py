import asyncio
from functools import wraps

def async_retry(func):
    """
    A no-op retry decorator for async functions.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper

class AsyncRetryContextManager:
    def __init__(self, history_collector=None):
        self.history = history_collector

    async def __aenter__(self):
        if self.history is not None:
            self.history.record({"event": "aenter", "time": asyncio.get_event_loop().time()})
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.history is not None:
            self.history.record({
                "event": "aexit",
                "time": asyncio.get_event_loop().time(),
                "exception": exc_type.__name__ if exc_type else None
            })
        return False
