import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as _FuturesTimeoutError
from .task import TaskState
from .metadata import MetadataStorage
from .alerting import AlertingService
from .context import ExecutionContext
from utils import retry_loop, record_metadata, wrap_alert

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

        # template metadata
        meta = {
            'status': TaskState.PENDING,
            'retries': 0,
            'start_time': None,
            'end_time': None,
            'execution_time': None,
            'exception': None,
        }

        for attempt, result, exc in retry_loop(
            func=lambda ctx, **kwargs: 
                self.executor.submit(task.func, ctx, **kwargs).result(timeout=task.timeout) 
                if task.timeout else task.func(self.context, **{k:self.context[k] for k in task.input_keys}),
            args=(self.context,),
            kwargs={},
            max_retries=task.max_retries,
            delay=task.retry_delay_seconds,
            backoff_factor=task.backoff_factor,
            timeout=None,
            sleep_func=self.sleep
        ):
            meta['start_time'] = time.time()
            meta['retries'] = attempt - 1
            if exc is None:
                # unpack outputs
                if task.output_keys:
                    outputs = result if isinstance(result, dict) else dict(zip(task.output_keys, result if hasattr(result,'__iter__') else [result]))
                    for k,v in outputs.items():
                        self.context[k] = v
                meta['status'] = TaskState.SUCCESS
                meta['end_time'] = time.time()
                record_metadata(self.metadata_storage, task.name, meta['status'], meta['retries'], meta['start_time'], meta['end_time'])
                return result
            else:
                meta['status'] = TaskState.RUNNING if attempt <= task.max_retries else TaskState.FAILURE
                meta['exception'] = exc
                meta['end_time'] = time.time()
                record_metadata(self.metadata_storage, task.name, meta['status'], meta['retries'], meta['start_time'], meta['end_time'], exc)
                if attempt > task.max_retries:
                    wrap_alert(self.alerting_service, task.name, exc, meta)
                    raise TaskExecutionError(task.name, exc, meta)
