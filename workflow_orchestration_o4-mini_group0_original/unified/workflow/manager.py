"""
WorkflowManager handles task scheduling, prioritization, execution, and state tracking.
"""
import heapq
from threading import Lock
from typing import Dict, List, Optional
from .task import Task, TaskState

class WorkflowManager:
    def __init__(self):
        self._lock = Lock()
        self._queue: List[Task] = []
        self._tasks: Dict[str, Task] = {}

    def add_task(self, task: Task):
        """
        Add a task to the manager.
        """
        with self._lock:
            if task.task_id in self._tasks:
                raise ValueError(f"Task with id {task.task_id} already exists")
            heapq.heappush(self._queue, task)
            self._tasks[task.task_id] = task

    def run_all(self):
        """
        Run all tasks in priority order. Dynamically created tasks also get executed.
        """
        while True:
            with self._lock:
                if not self._queue:
                    break
                task = heapq.heappop(self._queue)
            dynamic_tasks = task.run()
            # register dynamic tasks
            for dt in dynamic_tasks:
                self.add_task(dt)

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def get_all_states(self) -> Dict[str, str]:
        return {tid: t.state for tid, t in self._tasks.items()}