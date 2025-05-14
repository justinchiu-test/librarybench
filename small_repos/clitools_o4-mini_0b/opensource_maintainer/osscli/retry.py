import time
import functools

def retry_call(tries=3, backoff=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mtries, mbackoff = tries, backoff
            last_exc = None
            for attempt in range(1, mtries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    time.sleep(mbackoff)
                    mbackoff *= 2
            raise last_exc
        return wrapper
    return decorator
