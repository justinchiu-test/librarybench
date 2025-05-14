import time
import functools
from . import config

class Processor:
    def process(self, record):
        raise NotImplementedError("Processor subclasses must implement process()")

def validate_schema(record, schema):
    # Simple schema validation: check required keys
    required = schema.get('required', [])
    for key in required:
        if key not in record:
            return False
    return True

def retry_on_error(times, backoff=0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if backoff and attempt < times:
                        time.sleep(backoff)
            # If we exit loop, re-raise last exception
            raise last_exc
        return wrapper
    return decorator

def halt_on_error(func):
    # Pass-through decorator: errors propagate immediately
    return func
