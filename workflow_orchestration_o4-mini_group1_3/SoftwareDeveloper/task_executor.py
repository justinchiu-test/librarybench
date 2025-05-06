import time
import concurrent.futures
from .errors import TaskExecutionError
from .task_executor import FutureTimeoutError
from utils import is_future_timeout

class TaskExecutor:
    def __init__(self, max_workers=None):
        self._tasks = {}
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def register_task(self, task):
        self._tasks[task.name] = task

    def execute(self, task_name, inputs=None):
        task = self._tasks[task_name]
        ctx = {} if inputs is None else dict(inputs)
        last_exception = None
        attempts = task.max_retries + 1

        for attempt in range(1, attempts + 1):
            future = self._executor.submit(task.func, ctx)
            try:
                result = future.result(timeout=task.timeout)
                for k in task.output_keys:
                    ctx[k] = result[k]
                return ctx
            except Exception as e:
                if is_future_timeout(e):
                    last_exception = FutureTimeoutError(
                        f"Task '{task.name}' timeout after {task.timeout} seconds"
                    )
                else:
                    last_exception = e

            if attempt < attempts:
                time.sleep(task.retry_delay_seconds)

        # final wrap for any leftover timeouts
        if is_future_timeout(last_exception):
            last_exception = FutureTimeoutError(
                f"Task '{task.name}' timeout after {task.timeout} seconds"
            )
        raise TaskExecutionError(
            f"Task '{task.name}' failed after {task.max_retries} retries: ",
            original_exception=last_exception
        )
