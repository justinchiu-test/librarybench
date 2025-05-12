import logging
import functools

def skip_on_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.warning(f"Skipping record due to error: {e}")
            return None
    return wrapper
