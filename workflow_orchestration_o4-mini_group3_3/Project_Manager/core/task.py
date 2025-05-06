import time
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from core.logger import logger

class TaskStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Task:
    def __init__(
        self, name, func, dependencies=None,
        timeout=None, max_retries=0, retry_delay_seconds=0
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
        self.attempts = 0
        while self.attempts <= self.max_retries:
            self.attempts += 1
            self.status = TaskStatus.RUNNING
            self.start_time = time.time()
            logger.info(f"Task {self.name} attempt {self.attempts} started.")
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self.func)
                try:
                    future.result(timeout=self.timeout)
                    self.status = TaskStatus.SUCCESS
                    logger.info(f"Task {self.name} succeeded.")
                    break
                except TimeoutError:
                    self.status = TaskStatus.FAILED
                    self.last_exception = TimeoutError(f"Task {self.name} timed out.")
                    logger.error(f"Task {self.name} timed out on attempt {self.attempts}.")
                except Exception:
                    self.status = TaskStatus.FAILED
                    self.last_exception = traceback.format_exc()
                    logger.error(f"Task {self.name} failed on attempt {self.attempts}: {self.last_exception}")
            self.end_time = time.time()
            if self.status == TaskStatus.SUCCESS:
                break
            if self.attempts <= self.max_retries:
                backoff = self.retry_delay_seconds * (2 ** (self.attempts - 1))
                logger.info(f"Task {self.name} retrying after {backoff} seconds backoff.")
                time.sleep(backoff)
        self.end_time = time.time()
        return self.status

    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
