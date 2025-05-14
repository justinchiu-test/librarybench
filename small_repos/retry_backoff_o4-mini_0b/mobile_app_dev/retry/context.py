import time
import asyncio
from .circuit_breaker import CircuitBreakerOpenException

class RetryContext:
    def __init__(self, strategy, stop_condition, on_retry=None, after_attempt=None, on_give_up=None, circuit_breaker=None):
        self.strategy = strategy
        self.stop_condition = stop_condition
        self.on_retry = on_retry
        self.after_attempt = after_attempt
        self.on_give_up = on_give_up
        self.circuit_breaker = circuit_breaker

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def run(self, func, *args, **kwargs):
        attempt = 0
        while True:
            attempt += 1
            if self.circuit_breaker:
                self.circuit_breaker.before_call()
            start = time.time()
            try:
                result = func(*args, **kwargs)
                latency = time.time() - start
                if self.after_attempt:
                    self.after_attempt(attempt, True, None, latency)
                if self.circuit_breaker:
                    self.circuit_breaker.after_call(True)
                return result
            except Exception as e:
                latency = time.time() - start
                if self.after_attempt:
                    self.after_attempt(attempt, False, e, latency)
                if self.circuit_breaker:
                    self.circuit_breaker.after_call(False)
                if self.stop_condition.should_stop(attempt, e):
                    if self.on_give_up:
                        self.on_give_up(e)
                    raise
                delay = self.strategy.delay(attempt)
                if self.on_retry:
                    self.on_retry(attempt, delay)
                time.sleep(delay)

    async def run_async(self, func, *args, **kwargs):
        attempt = 0
        while True:
            attempt += 1
            if self.circuit_breaker:
                self.circuit_breaker.before_call()
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                latency = time.time() - start
                if self.after_attempt:
                    self.after_attempt(attempt, True, None, latency)
                if self.circuit_breaker:
                    self.circuit_breaker.after_call(True)
                return result
            except Exception as e:
                latency = time.time() - start
                if self.after_attempt:
                    self.after_attempt(attempt, False, e, latency)
                if self.circuit_breaker:
                    self.circuit_breaker.after_call(False)
                if self.stop_condition.should_stop(attempt, e):
                    if self.on_give_up:
                        self.on_give_up(e)
                    raise
                delay = self.strategy.delay(attempt)
                if self.on_retry:
                    self.on_retry(attempt, delay)
                await asyncio.sleep(delay)

def retry_context(strategy, stop_condition, on_retry=None, after_attempt=None, on_give_up=None, circuit_breaker=None):
    return RetryContext(strategy, stop_condition, on_retry, after_attempt, on_give_up, circuit_breaker)
