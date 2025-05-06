from core.logger import logger
from core.task import TaskStatus
from utils import topological_sort

class Workflow:
    def __init__(self, name, version=1):
        self.name = name
        self.version = version
        self.tasks = {}  # name -> Task
        self.last_status = None
        self.last_run_details = {}

    def add_task(self, task):
        if task.name in self.tasks:
            raise ValueError(f"Task {task.name} already exists in workflow.")
        self.tasks[task.name] = task

    def bump_version(self):
        self.version += 1

    def run(self):
        logger.info(f"Workflow {self.name} v{self.version} starting.")
        order = topological_sort(self.tasks)
        self.last_run_details = {}
        for name in order:
            task = self.tasks[name]
            if any(self.tasks[d].status != TaskStatus.SUCCESS for d in task.dependencies):
                task.status = TaskStatus.FAILED
                logger.error(f"Task {name} skipped due to failed dependency.")
            else:
                status = task.execute({})
                self.last_run_details[name] = {
                    "status": status,
                    "attempts": task.attempts,
                    "duration": task.duration()
                }
        self.last_status = (TaskStatus.SUCCESS if
            all(t.status == TaskStatus.SUCCESS for t in self.tasks.values())
            else TaskStatus.FAILED)
        logger.info(f"Workflow {self.name} completed with status {self.last_status}.")
        return self.last_status
