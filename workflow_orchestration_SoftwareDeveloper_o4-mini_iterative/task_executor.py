import time
import concurrent.futures
from .errors import TaskExecutionError

# Define a distinct FutureTimeoutError so tests can see it and
# its message can include "timeout"
class FutureTimeoutError(Exception):
    """Raised when a task run via Future.result() times out."""
    pass

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
        # allow initial attempt + retries
        attempts = task.max_retries + 1
        for attempt in range(1, attempts + 1):
            future = self._executor.submit(task.func, ctx)
            try:
                # This may raise either concurrent.futures.TimeoutError or built-in TimeoutError
                result = future.result(timeout=task.timeout)
                # assume result is a dict of outputs
                for k in task.output_keys:
                    ctx[k] = result[k]
                return ctx
            except Exception as e:
                # Wrap any timeout in our FutureTimeoutError
                if isinstance(e, concurrent.futures.TimeoutError) or isinstance(e, TimeoutError):
                    last_exception = FutureTimeoutError(
                        f"Task '{task.name}' timeout after {task.timeout} seconds"
                    )
                else:
                    last_exception = e

            # if we have more retries left, wait and retry
            if attempt < attempts:
                time.sleep(task.retry_delay_seconds)

        # All attempts exhausted: ensure timeouts are always wrapped
        if isinstance(last_exception, (concurrent.futures.TimeoutError, TimeoutError)):
            last_exception = FutureTimeoutError(
                f"Task '{task.name}' timeout after {task.timeout} seconds"
            )

        # Wrap and re-raise
        raise TaskExecutionError(
            f"Task '{task.name}' failed after {task.max_retries} retries: ",
            original_exception=last_exception
        )
