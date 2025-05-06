"""
Task abstraction with retry support and state tracking.
"""
from enum import Enum, auto
from IT_Administrator.it_manager.exceptions import MaxRetriesExceeded
from utils import run_with_timeout

class TaskState(Enum):
    PENDING = auto()
    SUCCESS = auto()
    FAILED = auto()

class Task:
    def __init__(self, func, name=None, timeout=None, max_retries=0):
        """
        func         : callable to execute
        name         : optional name; defaults to func.__name__
        timeout      : maximum seconds to allow for func execution
        max_retries  : number of retries after the first failure (0 means no retry)
        """
        self.func = func
        self.name = name or func.__name__
        self.timeout = timeout
        self.max_retries = max_retries
        self.attempts = 0
        self.state = TaskState.PENDING
        self.result = None

    def run(self, *args, **kwargs):
        """
        Execute the task, retrying up to `max_retries` times on exception or timeout.
        On success, returns the func(*args,**kwargs) result and sets state to SUCCESS.
        On final failure, sets state to FAILED and raises MaxRetriesExceeded.
        """
        self.attempts = 0
        last_exc = None

        for _ in range(self.max_retries + 1):
            self.attempts += 1
            try:
                if self.timeout is not None:
                    value = run_with_timeout(self.func, self.timeout, *args, **kwargs)
                else:
                    value = self.func(*args, **kwargs)
                self.state = TaskState.SUCCESS
                self.result = value
                return value
            except Exception as e:
                last_exc = e

        self.state = TaskState.FAILED
        raise MaxRetriesExceeded(
            f"Task '{self.name}' exceeded max retries ({self.max_retries})"
        ) from last_exc
