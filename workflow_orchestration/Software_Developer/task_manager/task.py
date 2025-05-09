import time
import concurrent.futures

class Task:
    def __init__(self, name, func,
                 max_retries=0,
                 retry_delay_seconds=0,
                 timeout=None):
        self.name = name
        self.func = func
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.timeout = timeout
        self.dependencies = []

    def add_dependency(self, task):
        """
        Add a Task instance that this task depends on.
        """
        self.dependencies.append(task)

    def run(self):
        """
        Execute the task, honoring timeout, retries, and retry_delay_seconds.
        Returns the raw return value of self.func(), or raises the exception
        if it fails (after retries or timeout).
        """
        attempts = 0
        last_exc = None

        while True:
            attempts += 1
            try:
                if self.timeout is not None:
                    # run in threadpool to enforce timeout
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(self.func)
                        result = future.result(timeout=self.timeout)
                else:
                    result = self.func()
                return result

            except Exception as e:
                last_exc = e
                # If we've used up all retries, re‐raise
                if attempts > self.max_retries:
                    raise e
                # else, wait and retry
                if self.retry_delay_seconds:
                    time.sleep(self.retry_delay_seconds)
