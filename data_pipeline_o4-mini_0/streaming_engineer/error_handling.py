import time
import functools

def retry_on_exception(retries, backoff_seconds):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt >= retries:
                        raise
                    time.sleep(backoff_seconds)
                    attempt += 1
        return wrapper
    return decorator

def fallback(default_value):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                return default_value
        return wrapper
    return decorator
