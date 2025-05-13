"""
Retry decorator for Open Source Maintainer CLI.
"""
def retry_call(tries=3, backoff=1):
    import time
    def decorator(func):
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