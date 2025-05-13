"""
Utility functions for DevOps Engineer CLI.
"""
import datetime
import uuid
import re
import os
import time

def compute_default(kind):
    if kind == 'timestamp':
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    if kind == 'uuid':
        return str(uuid.uuid4())
    raise ValueError(f"Unknown default: {kind}")

def range_validator(min_value, max_value):
    def validator(val):
        try:
            num = int(val)
        except Exception:
            raise ValueError(f"Not an integer: {val}")
        if num < min_value or num > max_value:
            raise ValueError(f"Out of range: {val}")
        return True
    return validator

def file_exists(path):
    if os.path.exists(path):
        return True
    raise FileNotFoundError(path)

def regex_validator(pattern):
    prog = re.compile(pattern)
    def validator(val):
        if prog.fullmatch(val):
            return True
        raise ValueError(f"Does not match pattern: {val}")
    return validator

def retry_call(max_attempts, base_delay):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    time.sleep(base_delay)
        return wrapper
    return decorator