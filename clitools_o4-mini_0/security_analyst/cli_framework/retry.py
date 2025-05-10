import time
import random

def retry_call(func, *args, retries=3, base_delay=0.1, **kwargs):
    attempt = 0
    while True:
        try:
            return func(*args, **kwargs)
        except Exception:
            if attempt >= retries:
                raise
            delay = base_delay * (2 ** attempt) * (1 + random.random())
            time.sleep(delay)
            attempt += 1
