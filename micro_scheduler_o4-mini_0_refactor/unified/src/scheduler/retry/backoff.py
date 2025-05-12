"""
Backoff strategies for retry logic.
"""
from functools import wraps
import time

class BackoffStrategy:
    """Callable backoff strategy."""
    def __init__(self, initial=1, factor=2, max_delay=None):
        self.initial = initial
        self.factor = factor
        self.max_delay = max_delay
    def __call__(self, attempt):
        delay = self.initial * (self.factor ** attempt)
        if self.max_delay is not None:
            return min(delay, self.max_delay)
        return delay

def exponential_backoff(func=None, *, initial=1, factor=2, max_delay=None, max_retries=1):
    """
    Decorator for retrying a function with exponential backoff.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt >= max_retries:
                        raise
                    delay = initial * (factor ** attempt)
                    if max_delay is not None:
                        delay = min(delay, max_delay)
                    time.sleep(delay)
                    attempt += 1
        return wrapper
    if func is None:
        return decorator
    else:
        return decorator(func)