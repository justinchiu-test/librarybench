import time
import asyncio
from retry.backoff import BackoffGeneratorInterface
from retry.stop_condition import MaxAttemptsStopCondition

class RetryManager:
    def __init__(
        self,
        backoff_strategy: BackoffGeneratorInterface,
        stop_condition: MaxAttemptsStopCondition,
        hooks: list = None,
        context: dict = None,
        sleep_func=None,
        async_sleep_func=None
    ):
        self.backoff = backoff_strategy
        self.stop_condition = stop_condition
        self.hooks = hooks or []
        self.context = context or {}
        self.sleep = sleep_func if sleep_func is not None else time.sleep
        self.async_sleep = async_sleep_func if async_sleep_func is not None else asyncio.sleep

    # synchronous context manager
    def __enter__(self):
        for hook in self.hooks:
            if hasattr(hook, 'on_start'):
                hook.on_start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    # asynchronous context manager support
    async def __aenter__(self):
        for hook in self.hooks:
            if hasattr(hook, 'on_start'):
                hook.on_start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    def call(self, func, *args, **kwargs):
        attempt = 1
        while True:
            try:
                result = func(*args, **kwargs)
                for hook in self.hooks:
                    if hasattr(hook, 'on_success'):
                        hook.on_success(attempt, result, self.context)
                return result
            except Exception as ex:
                if self.stop_condition.should_stop(attempt):
                    for hook in self.hooks:
                        if hasattr(hook, 'on_failure'):
                            hook.on_failure(attempt, ex, self.context)
                    raise
                delay = self.backoff.get_delay(attempt)
                for hook in self.hooks:
                    if hasattr(hook, 'on_retry'):
                        hook.on_retry(attempt, ex, delay, self.context)
                attempt += 1
                self.sleep(delay)

    async def call_async(self, func, *args, **kwargs):
        attempt = 1
        while True:
            try:
                result = await func(*args, **kwargs)
                for hook in self.hooks:
                    if hasattr(hook, 'on_success'):
                        hook.on_success(attempt, result, self.context)
                return result
            except Exception as ex:
                if self.stop_condition.should_stop(attempt):
                    for hook in self.hooks:
                        if hasattr(hook, 'on_failure'):
                            hook.on_failure(attempt, ex, self.context)
                    raise
                delay = self.backoff.get_delay(attempt)
                for hook in self.hooks:
                    if hasattr(hook, 'on_retry'):
                        hook.on_retry(attempt, ex, delay, self.context)
                attempt += 1
                await self.async_sleep(delay)
