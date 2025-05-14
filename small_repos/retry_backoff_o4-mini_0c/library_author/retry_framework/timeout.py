import signal
from functools import wraps

class TimeoutError(Exception):
    pass

def _handler(signum, frame):
    raise TimeoutError("Operation timed out")

def timeout_per_attempt(seconds):
    """
    Decorator to timeout a function if it runs longer than 'seconds'.
    Works on UNIX systems.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Immediately timeout on non-positive timeout
            if seconds <= 0:
                raise TimeoutError("Operation timed out")
            original_handler = signal.getsignal(signal.SIGALRM)
            signal.signal(signal.SIGALRM, _handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)
            return result
        return wrapper
    return decorator
