from datetime import datetime
from .context import ExecutionContext
from .metadata import MetadataStorage
from .alerting import Alerting
from .exceptions import TaskFailureError, TaskTimeoutError
from utils import retry_loop, compute_backoff

class Pipeline:
    def __init__(self):
        self.tasks = []
        self.context = ExecutionContext()
        self.metadata = MetadataStorage()
        self.alerting = Alerting()

    def add_task(self, task):
        self.tasks.append(task)

    def run(self):
        idx = 0
        while idx < len(self.tasks):
            task = self.tasks[idx]
            start = datetime.utcnow()
            try:
                for attempt, result, exc in retry_loop(
                    func=task.run,
                    args=(self.context,),
                    max_retries=task.max_retries,
                    delay=task.retry_delay_seconds,
                    backoff_factor=task.backoff_factor,
                    timeout=task.timeout_seconds,
                    sleep_func=task._sleep
                ):
                    if exc is None:
                        task.state = 'success'
                        self.context.set(task.task_id, result)
                        break
                    else:
                        task.state = 'running' if attempt <= task.max_retries else 'failure'
                        if attempt > task.max_retries:
                            raise (TaskTimeoutError(result) if isinstance(exc, TimeoutError) else TaskFailureError(result))
                # record success
            except Exception as e:
                task.state = 'failure'
                msg = f"Task {task.task_id} failed: {e}"
                self.alerting.notify(msg)
            end = datetime.utcnow()
            status = task.state
            self.metadata.record(task.task_id, start, end, status)
            for dyn in self.context.pop_dynamic_tasks():
                self.add_task(dyn)
            idx += 1
        return self.context
