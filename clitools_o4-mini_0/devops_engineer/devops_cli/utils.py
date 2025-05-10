import time
import random
import re
import os
from datetime import datetime
from uuid import uuid4
from functools import wraps

def compute_default(kind):
    if kind == "timestamp":
        return datetime.utcnow().isoformat() + "Z"
    if kind == "uuid":
        return str(uuid4())
    raise ValueError(f"Unknown default kind: {kind}")

def range_validator(min_value=None, max_value=None):
    def validate(x):
        if min_value is not None and x < min_value:
            raise ValueError(f"Value {x} < min {min_value}")
        if max_value is not None and x > max_value:
            raise ValueError(f"Value {x} > max {max_value}")
        return True
    return validate

def file_exists(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist")
    return True

def regex_validator(pattern):
    reg = re.compile(pattern)
    def validate(x):
        if not reg.match(x):
            raise ValueError(f"{x} does not match {pattern}")
        return True
    return validate

def retry_call(max_attempts=3, base_delay=0.1, max_delay=1.0):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempts - 1)))
                    delay = delay * (1 + random.random() * 0.1)
                    time.sleep(delay)
        return wrapper
    return decorator
