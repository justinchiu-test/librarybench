from collections import deque
from typing import Dict, List, Optional


class Task:
    def __init__(self, id: str, version: int = 1, dependencies: Optional[List[str]] = None):
        """
        A simple Task.  `dependencies` is a list of other task IDs that must
        complete before this one runs.
        """
        self.id = id
        self.version = version
        self.dependencies = dependencies or []
        self.status = "PENDING"

    def run(self):
        """
        Simulate running the task by marking it SUCCESS.
        """
        self.status = "SUCCESS"


class TaskQueue:
    def __init__(self):
        self._q = deque()  # FIFO

    def enqueue(self, task: Task):
        self._q.append(task)

    def dequeue(self) -> Task:
        if not self._q:
            raise IndexError("TaskQueue is empty")
        return self._q.popleft()

    def is_empty(self) -> bool:
        return not self._q


class Workflow:
    def __init__(self, id: str, tasks: List[Task], version: Optional[int] = None):
        """
        A workflow is just a collection of named Tasks.
        """
        self.id = id
        # map task.id -> Task object
        self.tasks: Dict[str, Task] = {t.id: t for t in tasks}

        # verify that every declared dependency exists
        for t in tasks:
            for dep in t.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"Task {t.id} has unknown dependency {dep}")

        # workflow version; if caller passed one, use it, else start at 1
        self.version = version if version is not None else 1

    def get_task(self, id: str) -> Optional[Task]:
        return self.tasks.get(id)


class WorkflowManager:
    def __init__(self):
        # keep track of the latest Workflow object by id
        self.workflows: Dict[str, Workflow] = {}
        # keep track of numeric version by workflow id
        self.versions: Dict[str, int] = {}

    def register_workflow(self, wf: Workflow):
        """
        Add or update a workflow.  If it's brand new, record its version.
        If it's the same id but a different task set, bump the version.
        If it's the same task set, keep the version.
        """
        wid = wf.id
        if wid not in self.workflows:
            # brand-new workflow
            self.workflows[wid] = wf
            self.versions[wid] = wf.version
        else:
            old = self.workflows[wid]
            # compare sets of task IDs
            if set(old.tasks.keys()) != set(wf.tasks.keys()):
                # tasks changed => bump
                self.versions[wid] += 1
                wf.version = self.versions[wid]
                self.workflows[wid] = wf
            else:
                # no change, preserve version
                wf.version = self.versions[wid]
                self.workflows[wid] = wf

    def get_version(self, workflow_id: str) -> Optional[int]:
        return self.versions.get(workflow_id)


class Scheduler:
    def __init__(self, manager: WorkflowManager):
        self.manager = manager
        self.queue = TaskQueue()

    def run(self, workflow_id: str):
        """
        Execute all tasks in the workflow, respecting dependencies.
        """
        if workflow_id not in self.manager.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        wf = self.manager.workflows[workflow_id]

        # reset statuses for a fresh run
        for t in wf.tasks.values():
            t.status = "PENDING"

        # enqueue tasks with no dependencies
        for t in wf.tasks.values():
            if not t.dependencies:
                self.queue.enqueue(t)

        # process
        while not self.queue.is_empty():
            task = self.queue.dequeue()
            if task.status != "PENDING":
                continue
            # run it
            task.run()
            # after running, see if any other tasks have now all deps satisfied
            for t in wf.tasks.values():
                if t.status == "PENDING":
                    if all(wf.tasks[dep].status == "SUCCESS" for dep in t.dependencies):
                        self.queue.enqueue(t)
