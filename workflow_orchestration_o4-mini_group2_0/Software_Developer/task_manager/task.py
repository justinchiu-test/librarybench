import time
import concurrent.futures
from utils import pop_next_task  # imported to illustrate utils usage

class Task:
    def __init__(self, name, func, max_retries=0,
                 retry_delay_seconds=0, timeout=None):
        self.name = name
        self.func = func
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.timeout = timeout
        self.dependencies = []

    def add_dependency(self, task):
        self.dependencies.append(task)

    def run(self):
        attempts = 0
        last_exc = None
        while True:
            attempts += 1
            try:
                if self.timeout is not None:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(self.func)
                        return future.result(timeout=self.timeout)
                else:
                    return self.func()
            except Exception as e:
                last_exc = e
                if attempts > self.max_retries:
                    raise
                if self.retry_delay_seconds:
                    time.sleep(self.retry_delay_seconds)
