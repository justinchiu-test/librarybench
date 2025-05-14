import time
import random
import functools

def retry(max_retries=3, base_delay=0.1, backoff=2, jitter=0):
    """
    Decorator for retrying a function upon exception with exponential backoff.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise
                    time.sleep(delay + random.uniform(0, jitter))
                    delay *= backoff
        return wrapper
    return decorator
