"""
Retry logic for Security Analyst CLI.
"""
def retry_call(func, retries=3, base_delay=1):
    import time
    attempts = 0
    while True:
        try:
            return func()
        except Exception:
            attempts += 1
            if attempts >= retries:
                raise
            time.sleep(base_delay)