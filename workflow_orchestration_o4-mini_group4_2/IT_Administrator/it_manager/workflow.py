from typing import List
from .version import VersionedEntity
from .tasks import Task, TaskState
from .exceptions import WorkflowFailure


class Workflow(VersionedEntity):
    """
    A workflow that manages a sequence of tasks, with versioning and failure propagation.
    """
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self._tasks: List[Task] = []
        self.save_version(self._tasks.copy())

    def add_task(self, task: Task):
        self._tasks.append(task)
        self.save_version(self._tasks.copy())

    @property
    def tasks(self):
        return list(self._tasks)

    def run(self):
        """
        Runs tasks in sequence, stops on failure and propagates.
        """
        for idx, task in enumerate(self._tasks):
            try:
                task.run()
            except Exception as e:
                # propagate failure: mark rest as pending, raise
                for t in self._tasks[idx + 1:]:
                    t.state = TaskState.PENDING
                raise WorkflowFailure(f"Workflow '{self.name}' failed on task '{task.name}': {e}") from e
        return [t.result for t in self._tasks]
