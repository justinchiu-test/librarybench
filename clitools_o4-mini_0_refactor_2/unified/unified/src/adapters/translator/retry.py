"""
Retry decorator for Translator CLI adapter.
"""
def retry(max_retries=3, base_delay=1, backoff=2, jitter=0):
    import time, random
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            delay = base_delay
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempts += 1
                    if attempts >= max_retries:
                        raise
                    time.sleep(delay + (random.random() * jitter))
                    delay *= backoff
        return wrapper
    return decorator