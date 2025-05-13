import time
import functools

def retry(times=3, delay=0, backoff=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mdelay = delay
            last_exc = None
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    time.sleep(mdelay)
                    mdelay *= backoff
            raise last_exc
        return wrapper
    return decorator
