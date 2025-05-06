import time
from core.logger import logger
from utils import execute_with_retries
from core.task import TaskStatus  # ensure TaskStatus is available

class Task:
    def __init__(
        self,
        name,
        func,
        dependencies=None,
        timeout=None,
        max_retries=0,
        retry_delay_seconds=0
    ):
        self.name = name
        self.func = func
        self.dependencies = set(dependencies) if dependencies else set()
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.status = TaskStatus.PENDING
        self.attempts = 0
        self.last_exception = None
        self.start_time = None
        self.end_time = None

    def execute(self, context):
        status, attempts, start, end, exc = execute_with_retries(
            self.func,
            self.timeout,
            self.max_retries,
            self.retry_delay_seconds,
            logger,
            self.name
        )
        self.status = status
        self.attempts = attempts
        self.start_time = start
        self.end_time = end
        self.last_exception = exc
        return self.status

    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
