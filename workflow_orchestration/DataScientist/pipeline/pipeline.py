from datetime import datetime
from .context import ExecutionContext
from .metadata import MetadataStorage
from .alerting import Alerting
from .exceptions import TaskFailureError, TaskTimeoutError

class Pipeline:
    def __init__(self):
        self.tasks = []
        self.context = ExecutionContext()
        self.metadata = MetadataStorage()
        self.alerting = Alerting()

    def add_task(self, task):
        self.tasks.append(task)

    def run(self):
        index = 0
        while index < len(self.tasks):
            task = self.tasks[index]
            start = datetime.utcnow()
            try:
                result = task.execute(self.context)
                # store outputs in context under task_id
                self.context.set(task.task_id, result)
                status = task.state
            except Exception as e:
                # notify on failure
                msg = f"Task {task.task_id} failed: {e}"
                self.alerting.notify(msg)
                status = 'failure'
            end = datetime.utcnow()
            # record metadata
            self.metadata.record(task.task_id, start, end, status)
            # after execution, collect dynamic tasks
            dyn = self.context.pop_dynamic_tasks()
            for dt in dyn:
                self.add_task(dt)
            index += 1
        return self.context
