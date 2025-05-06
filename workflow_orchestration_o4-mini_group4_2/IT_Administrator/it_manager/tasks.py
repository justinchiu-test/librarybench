"""
Task abstraction with retry support.
"""
import threading
from typing import Any, Callable, Tuple, Dict
from .exceptions import MaxRetriesExceeded, TaskTimeoutError
from .tasks import TaskState  # assume TaskState is defined in this module


class Task:
    def __init__(self, func: Callable, name: str = None, timeout: float = None, max_retries: int = 0):
        self.func = func
        self.name = name or func.__name__
        self.timeout = timeout
        self.max_retries = max_retries
        self.attempts = 0
        self.state = TaskState.PENDING
        self.result = None

    def run(self, *args, **kwargs):
        self.attempts = 0
        last_exc = None
        for _ in range(self.max_retries + 1):
            self.attempts += 1
            try:
                res = self._execute_with_timeout(*args, **kwargs)
                self.result = res
                self.state = TaskState.SUCCESS
                return res
            except Exception as e:
                last_exc = e
                self.state = TaskState.PENDING
        self.state = TaskState.FAILED
        raise MaxRetriesExceeded(f"Task '{self.name}' exceeded max retries ({self.max_retries})") from last_exc

    def _execute_with_timeout(self, *args, **kwargs):
        if self.timeout is None:
            return self.func(*args, **kwargs)
        result_container: Dict[str, Any] = {}
        exc_container: Dict[str, Any] = {}

        def target():
            try:
                result_container['value'] = self.func(*args, **kwargs)
            except Exception as ex:
                exc_container['error'] = ex

        th = threading.Thread(target=target)
        th.daemon = True
        th.start()
        th.join(self.timeout)
        if th.is_alive():
            raise TaskTimeoutError(f"Task '{self.name}' timed out after {self.timeout}s")
        if 'error' in exc_container:
            raise exc_container['error']
        return result_container.get('value')
