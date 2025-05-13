import time
from functools import wraps

def resilient(on_exceptions, retries=0, backoff_factor=0.0, callback=None):
    """
    Decorator to retry a function on specified exceptions.
    :param on_exceptions: tuple of exception classes to catch and retry on
    :param retries: number of retry attempts allowed
    :param backoff_factor: factor for exponential backoff (sleep = backoff_factor * attempt)
    :param callback: callable(exception, attempt) called on each caught exception before retry
    """
    def decorator(func):
        @wraps(func)
        def _wrapped(*args, **kwargs):
            attempt = 0
            while True:
                attempt += 1
                try:
                    return func(*args, **kwargs)
                except on_exceptions as ex:
                    # if we've exhausted retries, re-raise
                    if attempt > retries:
                        raise
                    # invoke callback if provided
                    if callback:
                        callback(ex, attempt)
                    # back off
                    if backoff_factor:
                        time.sleep(backoff_factor * attempt)
                    # retry
        return _wrapped
    return decorator
