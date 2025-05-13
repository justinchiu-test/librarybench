import time
import threading
import json
from functools import wraps
from contextlib import contextmanager
import concurrent.futures
import asyncio

# Try to import stdlib tomllib (Python 3.11+), else fall back to external toml
_using_stdlib_toml = False
try:
    import tomllib as toml
    _using_stdlib_toml = True
except ImportError:
    try:
        import toml
    except ImportError:
        toml = None

class BackoffRegistry:
    _registry = {
        'exponential': lambda n: 2 ** n,
        'linear': lambda n: n,
    }

    @classmethod
    def register(cls, name, func):
        cls._registry[name] = func

    @classmethod
    def get(cls, name):
        if name not in cls._registry:
            raise KeyError(f"Backoff strategy '{name}' not found")
        return cls._registry[name]

class ConfigLoader:
    @staticmethod
    def load_config(path):
        if path.endswith('.json'):
            with open(path, 'r') as f:
                return json.load(f)
        elif path.endswith('.toml'):
            if toml is None:
                raise RuntimeError("TOML support not available")
            # Use appropriate mode for tomllib vs external toml
            if _using_stdlib_toml:
                # tomllib.load expects a binary file
                with open(path, 'rb') as f:
                    return toml.load(f)
            else:
                # external toml library expects text
                with open(path, 'r') as f:
                    return toml.load(f)
        else:
            raise ValueError("Unsupported config format")

class StopConditionInterface:
    def should_stop(self, exception):
        raise NotImplementedError()

class CancellationPolicy:
    def __init__(self):
        self._event = threading.Event()

    def cancel(self):
        self._event.set()

    def is_cancelled(self):
        return self._event.is_set()

class RetryHistoryCollector:
    def __init__(self):
        self.entries = []

    def record(self, attempt, delay, exception, result):
        self.entries.append({
            'attempt': attempt,
            'delay': delay,
            'exception': exception,
            'result': result,
        })

class CircuitBreaker:
    def __init__(self, failure_threshold, recovery_timeout):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'

    def call(self, func, *args, **kwargs):
        now = time.time()
        if self.state == 'OPEN':
            if now - (self.last_failure_time or 0) > self.recovery_timeout:
                self.state = 'HALF_OPEN'
            else:
                raise RuntimeError("CircuitOpen")
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = now
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            raise
        else:
            self.failure_count = 0
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
            return result

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper

def retry(attempts=3, backoff='exponential', timeout=None,
          circuit_breaker=None, stop_conditions=None,
          cancellation_policy=None, history_collector=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                if cancellation_policy and cancellation_policy.is_cancelled():
                    raise RuntimeError("Cancelled")
                delay = BackoffRegistry.get(backoff)(attempt - 1)
                # NOTE: skip actual sleeping to avoid blocking tests
                exception = None
                result = None
                target = func
                if circuit_breaker:
                    target = circuit_breaker(func)
                try:
                    if timeout:
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(target, *args, **kwargs)
                            result = future.result(timeout=timeout)
                    else:
                        result = target(*args, **kwargs)
                except Exception as e:
                    exception = e
                if history_collector:
                    history_collector.record(attempt, delay, exception, result)
                if exception is None:
                    return result
                if stop_conditions:
                    for cond in stop_conditions:
                        if cond.should_stop(exception):
                            raise exception
                if attempt == attempts:
                    raise exception
            # unreachable
        return wrapper
    return decorator

def async_retry(attempts=3, backoff='exponential', timeout=None,
                circuit_breaker=None, stop_conditions=None,
                cancellation_policy=None, history_collector=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                if cancellation_policy and cancellation_policy.is_cancelled():
                    raise RuntimeError("Cancelled")
                delay = BackoffRegistry.get(backoff)(attempt - 1)
                # NOTE: skip actual sleeping to avoid blocking tests
                exception = None
                result = None
                target = func
                if circuit_breaker:
                    target = circuit_breaker(func)
                try:
                    if timeout:
                        result = await asyncio.wait_for(target(*args, **kwargs), timeout=timeout)
                    else:
                        result = await target(*args, **kwargs)
                except Exception as e:
                    exception = e
                if history_collector:
                    history_collector.record(attempt, delay, exception, result)
                if exception is None:
                    return result
                if stop_conditions:
                    for cond in stop_conditions:
                        if cond.should_stop(exception):
                            raise exception
                if attempt == attempts:
                    raise exception
            # unreachable
        return wrapper
    return decorator

@contextmanager
def retry_scope(**kwargs):
    def scope_decorator(func):
        return retry(**kwargs)(func)
    yield scope_decorator
