"""
Task abstraction with retry support, timeout, and state tracking.
"""

import time
from enum import Enum
from typing import Any
from .exceptions import MaxRetriesExceeded, TaskTimeoutError
from utils import run_with_retry

class TaskState(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Task:
    def __init__(self, func, name=None, timeout=None, max_retries=0):
        """
        func         : callable to execute
        name         : optional name; defaults to func.__name__
        timeout      : seconds allowed for each attempt
        max_retries  : number of retries after the first failure (0 means no retry)
        """
        self.func = func
        self.name = name or func.__name__
        self.timeout = timeout
        self.max_retries = max_retries
        self.attempts = 0
        self.state = TaskState.PENDING
        self.result = None

    def run(self, *args, **kwargs) -> Any:
        """
        Execute the task with retry and timeout. Updates state, attempts, and result.
        On final failure raises MaxRetriesExceeded.
        """
        try:
            res, attempts = run_with_retry(
                self.func, args, kwargs, self.timeout, self.max_retries, self.name
            )
            self.attempts = attempts
            self.result = res
            self.state = TaskState.SUCCESS
            return res
        except MaxRetriesExceeded:
            self.attempts = self.max_retries + 1
            self.state = TaskState.FAILED
            raise
