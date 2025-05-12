"""
Retry decorator for translator operations.
"""
import time
import random
import functools

def retry(max_retries, base_delay=0, backoff=1, jitter=0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            delay = base_delay
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempts += 1
                    if attempts > max_retries:
                        raise
                    # delay with backoff and jitter
                    time.sleep(delay + random.uniform(0, jitter))
                    delay *= backoff
        return wrapper
    return decorator