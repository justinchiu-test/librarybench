import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from .task import TaskState
from .metadata import MetadataStorage
from .alerting import AlertingService
from .context import ExecutionContext
from utils import compute_delay

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
        self.tasks[task.name] = task

    def execute(self, task_name):
        if task_name not in self.tasks:
            raise KeyError(f"Task '{task_name}' is not registered")
        task = self.tasks[task_name]
        retries = 0
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
                kwargs = {k: self.context[k] for k in task.input_keys}
                future = self.executor.submit(task.func, self.context, **kwargs)
                result = future.result(timeout=task.timeout)

                if task.output_keys:
                    if isinstance(result, dict):
                        outputs = result
                    else:
                        if len(task.output_keys) == 1:
                            outputs = {task.output_keys[0]: result}
                        else:
                            outputs = dict(zip(task.output_keys, result))
                    for k, v in outputs.items():
                        self.context[k] = v

                metadata['status'] = TaskState.SUCCESS
                metadata['retries'] = retries
                metadata['end_time'] = time.time()
                metadata['execution_time'] = metadata['end_time'] - metadata['start_time']
                self.metadata_storage.append(task_name, metadata.copy())
                return result

            except FutureTimeoutError as e:
                exc = e
            except Exception as e:
                exc = e

            metadata['exception'] = exc
            metadata['retries'] = retries
            metadata['end_time'] = time.time()
            metadata['execution_time'] = metadata['end_time'] - metadata['start_time']
            self.metadata_storage.append(task_name, metadata.copy())

            if retries >= task.max_retries:
                metadata['status'] = TaskState.FAILURE
                self.alerting_service.send_alert(task_name, exc, metadata.copy())
                raise TaskExecutionError(task_name, exc, metadata.copy())

            retries += 1
            delay = compute_delay(task.retry_delay_seconds,
                                  task.backoff_factor,
                                  retries)
            self.sleep(delay)
