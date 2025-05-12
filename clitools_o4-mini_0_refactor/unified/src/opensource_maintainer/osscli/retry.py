"""
Retry decorator for open-source maintainers.
"""
import time
import functools

def retry_call(tries, backoff=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempts += 1
                    if attempts >= tries:
                        raise
                    time.sleep(backoff)
        return wrapper
    return decorator