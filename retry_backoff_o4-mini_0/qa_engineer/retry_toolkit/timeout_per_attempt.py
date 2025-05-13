import threading
import functools

class TimeoutError(Exception):
    pass

def timeout_per_attempt(timeout):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exc = [None]
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exc[0] = e
            t = threading.Thread(target=target)
            t.daemon = True
            t.start()
            t.join(timeout)
            if t.is_alive():
                raise TimeoutError("Function call timed out")
            if exc[0]:
                raise exc[0]
            return result[0]
        return wrapper
    return decorator
