import time
import threading
from heapq import heappush, heappop
from .models import Task, TaskState
from .utils import execute_task

class TaskManager:
    def __init__(self):
        self._queue = []              # heap of (−priority, Task)
        self._lock = threading.Lock()
        self.tasks = {}               # id -> Task

    def add_task(self, task: Task):
        """
        Add a Task to the manager's priority queue.
        Higher priority tasks (bigger integer) are run first.
        """
        with self._lock:
            heappush(self._queue, (-task.priority, task))
            self.tasks[task.id] = task

    def get_task(self, task_id: str) -> Task:
        return self.tasks.get(task_id)

    def run_all(self):
        """
        Run all tasks in the queue, in priority order, applying retry policies
        with exponential backoff. Retries re‐enqueue the task; failures stop.
        """
        while True:
            with self._lock:
                if not self._queue:
                    break
                _, task = heappop(self._queue)

            # perform a single execution attempt
            execute_task(task)

            # if task still pending, apply exponential backoff and requeue
            if task.state == TaskState.PENDING:
                delay = task.retry_policy.retry_delay_seconds * (2 ** (task.retries_done - 1))
                time.sleep(delay)
                with self._lock:
                    heappush(self._queue, (-task.priority, task))
