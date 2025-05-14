import time
from contextlib import contextmanager

@contextmanager
def timeout_per_attempt(seconds):
    start = time.time()
    yield
    elapsed = time.time() - start
    if elapsed > seconds:
        raise TimeoutError(f"Operation timed out after {elapsed:.2f}s")
