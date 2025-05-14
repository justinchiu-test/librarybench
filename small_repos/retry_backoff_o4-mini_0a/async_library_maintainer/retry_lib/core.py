import time
import asyncio
import inspect
from functools import wraps
from .strategies import FullJitterBackoffStrategy
from .conditions import MaxAttemptsStopCondition
from .context import get_all_context
from .hooks import RetryHook

class Retry:
    def __init__(self, stop=None, strategy=None, hooks=None):
        self.stop = stop or MaxAttemptsStopCondition()
        self.strategy = strategy or FullJitterBackoffStrategy()
        self.hooks = hooks or []

    def __enter__(self):
        # In a sync context manager, return a runner that applies the retry logic immediately
        def runner(func, *args, **kwargs):
            wrapped = self(func)
            return wrapped(*args, **kwargs)
        return runner

    def __exit__(self, exc_type, exc, tb):
        return False

    async def __aenter__(self):
        # In an async context manager, return a runner that applies retry logic,
        # returning either a direct result or a coroutine for async functions
        def runner(func, *args, **kwargs):
            wrapped = self(func)
            return wrapped(*args, **kwargs)
        return runner

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def __call__(self, func):
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def wrapped_async(*args, **kwargs):
                return await self._execute_async(func, *args, **kwargs)
            return wrapped_async
        else:
            @wraps(func)
            def wrapped_sync(*args, **kwargs):
                return self._execute_sync(func, *args, **kwargs)
            return wrapped_sync

    def _execute_sync(self, func, *args, **kwargs):
        delays = self.strategy()
        attempt = 0
        while True:
            try:
                attempt += 1
                return func(*args, **kwargs)
            except Exception as e:
                if self.stop.should_stop(attempt, e):
                    raise
                delay = next(delays)
                self._fire_hooks(attempt, e, delay)
                time.sleep(delay)

    async def _execute_async(self, func, *args, **kwargs):
        delays = self.strategy()
        attempt = 0
        while True:
            try:
                attempt += 1
                return await func(*args, **kwargs)
            except Exception as e:
                if self.stop.should_stop(attempt, e):
                    raise
                delay = next(delays)
                self._fire_hooks(attempt, e, delay)
                await asyncio.sleep(delay)

    def _fire_hooks(self, attempt, exception, delay):
        context = get_all_context()
        for hook in self.hooks:
            if isinstance(hook, RetryHook):
                hook.on_retry(attempt, exception, delay, context)
