import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from .task import TaskState
from .metadata import MetadataStorage
from .alerting import AlertingService
from .context import ExecutionContext
from .utils import (
    compute_backoff,
    is_future_timeout,
    wrap_future_timeout,
    apply_output_keys,
)

class TaskExecutionError(Exception):
    def __init__(self, task_name, original_exception, metadata):
        msg = f"Task '{task_name}' failed after retries: {original_exception}"
        super().__init__(msg)
        self.task_name = task_name
        self.original_exception = original_exception
        self.metadata = metadata

class TaskExecutor:
    def __init__(self,
                 tasks=None,
                 context=None,
                 metadata_storage=None,
                 alerting_service=None,
                 sleep_func=None):
        self.tasks = tasks or {}
        self.context = context or ExecutionContext()
        self.metadata_storage = metadata_storage or MetadataStorage()
        self.alerting_service = alerting_service or AlertingService()
        self.sleep = sleep_func or time.sleep
        self.executor = ThreadPoolExecutor(max_workers=10)

    def register_task(self, task):
        """Register (or override) a Task object under its name."""
        self.tasks[task.name] = task

    def execute(self, task_name):
        if task_name not in self.tasks:
            raise KeyError(f"Task '{task_name}' is not registered")
        task = self.tasks[task_name]
        retries = 0

        # prepare metadata template
        metadata = {
            'status': TaskState.PENDING,
            'retries': 0,
            'start_time': None,
            'end_time': None,
            'execution_time': None,
            'exception': None,
        }

        while True:
            metadata['start_time'] = time.time()
            metadata['status'] = TaskState.RUNNING
            metadata['exception'] = None
            try:
                # gather inputs
                kwargs = {k: self.context[k] for k in task.input_keys}
                future = self.executor.submit(task.func, self.context, **kwargs)
                result = future.result(timeout=task.timeout)
                # write outputs
                if task.output_keys:
                    apply_output_keys(self.context, result, task.output_keys)

                metadata.update({
                    'status': TaskState.SUCCESS,
                    'retries': retries,
                    'end_time': time.time(),
                })
                metadata['execution_time'] = metadata['end_time'] - metadata['start_time']
                self.metadata_storage.append(task_name, metadata.copy())
                return result

            except Exception as exc:
                # map timeout
                if is_future_timeout(exc):
                    last_exc = wrap_future_timeout(task.name, task.timeout)
                else:
                    last_exc = exc

            # record failure attempt
            metadata['exception'] = last_exc
            metadata['retries'] = retries
            metadata['end_time'] = time.time()
            metadata['execution_time'] = metadata['end_time'] - metadata['start_time']
            self.metadata_storage.append(task_name, metadata.copy())

            # decide retry or final failure
            if retries >= task.max_retries:
                metadata['status'] = TaskState.FAILURE
                self.alerting_service.send_alert(task_name, last_exc, metadata.copy())
                raise TaskExecutionError(task_name, last_exc, metadata.copy())

            # backoff then retry
            retries += 1
            delay = compute_backoff(task.retry_delay_seconds, task.backoff_factor, retries)
            self.sleep(delay)
