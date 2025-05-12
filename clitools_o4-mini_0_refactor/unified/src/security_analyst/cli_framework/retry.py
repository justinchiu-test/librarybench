"""
Retry logic for security analysts.
"""
import time

def retry_call(func, retries, base_delay):
    attempts = 0
    while True:
        try:
            return func()
        except Exception:
            attempts += 1
            if attempts >= retries:
                raise
            time.sleep(base_delay)