"""
Helpful utility functions: defaults, validators, retry logic.
"""
import time
import re
import os
import datetime
import uuid
import functools

def compute_default(kind):
    if kind == 'timestamp':
        # UTC timestamp in YYYYMMDDHHMMSSZ
        return datetime.datetime.utcnow().strftime('%Y%m%d%H%M%SZ')
    if kind == 'uuid':
        return str(uuid.uuid4())
    raise ValueError(f'Unknown default kind: {kind}')

def range_validator(min_val, max_val):
    def validator(val):
        if not (min_val <= val <= max_val):
            raise ValueError(f'Value {val} outside range [{min_val},{max_val}]')
        return True
    return validator

def file_exists(path):
    if os.path.exists(path):
        return True
    raise FileNotFoundError(f'File not found: {path}')

def regex_validator(pattern):
    compiled = re.compile(pattern)
    def validator(val):
        if not compiled.match(val):
            raise ValueError(f'Value {val} does not match pattern {pattern}')
        return True
    return validator

def retry_call(max_attempts=1, base_delay=0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    time.sleep(base_delay * attempts)
        return wrapper
    return decorator
 
def merge_dicts(a, b):
    """
    Recursively merge two dictionaries, returning a new dict.
    Values in b override those in a.
    """
    result = dict(a)
    for key, val in b.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = merge_dicts(result[key], val)
        else:
            result[key] = val
    return result