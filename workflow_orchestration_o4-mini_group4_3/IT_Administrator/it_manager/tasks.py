from enum import Enum
from .exceptions import MaxRetriesExceeded
from utils import run_with_timeout

class TaskState(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"

class Task:
    def __init__(self, func, name=None, timeout=None, max_retries=0):
        """
        func         : callable to execute
        name         : optional name; defaults to func.__name__
        timeout      : max seconds to wait for func; None means no timeout
        max_retries  : number of retries after the first failure
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
        Execute the task with timeout and retry support.
        """
        self.attempts = 0
        last_exc = None
        for _ in range(self.max_retries + 1):
            self.attempts += 1
            try:
                res = run_with_timeout(self.func, args, kwargs, self.timeout)
                self.state = TaskState.SUCCESS
                self.result = res
                return res
            except Exception as e:
                last_exc = e
                # retry if attempts remain
        self.state = TaskState.FAILURE
        raise MaxRetriesExceeded(
            f"Task '{self.name}' exceeded max retries ({self.max_retries})"
        ) from last_exc
