"""
Task abstraction with retry support.
"""

from .exceptions import MaxRetriesExceeded

class Task:
    def __init__(self, func, name=None, timeout=None, max_retries=0):
        """
        func         : callable to execute
        name         : optional name; defaults to func.__name__
        timeout      : not altered here, existing code may use it elsewhere
        max_retries  : number of retries after the first failure (0 means no retry)
        """
        self.func = func
        self.name = name or func.__name__
        self.timeout = timeout
        self.max_retries = max_retries
        self.attempts = 0

    def run(self, *args, **kwargs):
        """
        Execute the task, retrying up to `max_retries` times on exception.
        On success returns the func(*args,**kwargs) result.
        On final failure raises MaxRetriesExceeded wrapping the last exception.
        """
        self.attempts = 0
        last_exc = None

        # We allow max_retries retries, i.e. up to max_retries+1 total attempts
        for _ in range(self.max_retries + 1):
            self.attempts += 1
            try:
                return self.func(*args, **kwargs)
            except Exception as e:
                last_exc = e
                # loop around and retry if we still have attempts left

        # If we exhaust all attempts, raise our retry exception
        raise MaxRetriesExceeded(f"Task '{self.name}' exceeded max retries ({self.max_retries})") from last_exc
