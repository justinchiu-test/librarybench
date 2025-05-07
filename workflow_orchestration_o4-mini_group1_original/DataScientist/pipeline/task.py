import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime

from .backoff import exponential_backoff
from .exceptions import TaskTimeoutError, TaskFailureError

class Task:
    """
    Base Task class to be subclassed.
    """
    def __init__(
        self,
        task_id: str,
        max_retries: int = 0,
        retry_delay_seconds: float = 1.0,
        backoff_factor: float = 2.0,
        timeout_seconds: float = None
    ):
        self.task_id = task_id
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.backoff_factor = backoff_factor
        self.timeout_seconds = timeout_seconds
        self.state = 'pending'
        self.attempt = 0
        # overrideable sleep function (for tests)
        self._sleep = time.sleep

    def run(self, context):
        """
        Override this method with actual task logic.
        Should return result or raise Exception.
        """
        raise NotImplementedError

    def execute(self, context):
        from .alerting import Alerting  # avoid circular
        self.state = 'pending'
        last_exception = None
        for attempt in range(1, self.max_retries + 2):
            self.attempt = attempt
            self.state = 'running'
            start = datetime.utcnow()
            try:
                # run with timeout
                if self.timeout_seconds is not None:
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(self.run, context)
                        result = future.result(timeout=self.timeout_seconds)
                else:
                    result = self.run(context)
                # success
                end = datetime.utcnow()
                self.state = 'success'
                return result
            except FuturesTimeoutError:
                last_exception = TaskTimeoutError(f"Task {self.task_id} timed out")
            except Exception as e:
                last_exception = e
            end = datetime.utcnow()
            # if not last attempt, sleep then retry
            if attempt <= self.max_retries:
                delay = exponential_backoff(
                    self.retry_delay_seconds,
                    self.backoff_factor,
                    attempt
                )
                try:
                    self._sleep(delay)
                except Exception:
                    pass
                continue
            # all attempts exhausted
            self.state = 'failure'
            raise TaskFailureError(f"Task {self.task_id} failed after {self.attempt} attempts: {last_exception}")

