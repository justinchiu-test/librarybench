from datetime import datetime
from .context import ExecutionContext
from .metadata import MetadataStorage
from .alerting import Alerting
from .exceptions import TaskFailureError, TaskTimeoutError
from utils import exponential_backoff

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
                result = task.execute(self.context)
                self.context.set(task.task_id, result)
                status = task.state
            except TaskTimeoutError as e:
                status = 'failure'
                self.alerting.notify(str(e))
            except Exception as e:
                status = 'failure'
                self.alerting.notify(f"Task {task.task_id} failed: {e}")
            end = datetime.utcnow()
            self.metadata.record(task.task_id, start, end, status)
            for dyn in self.context.pop_dynamic_tasks():
                self.add_task(dyn)
            idx += 1
        return self.context
