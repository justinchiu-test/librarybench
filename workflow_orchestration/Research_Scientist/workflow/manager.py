import time
import threading
from heapq import heappush, heappop
from .models import Task, TaskState

class TaskManager:
    def __init__(self):
        self._queue = []
        self._lock = threading.Lock()
        self.tasks = {}  # maps task.id to Task

    def add_task(self, task: Task):
        """
        Add a Task to the manager's priority queue.
        Higher priority tasks (bigger integer) are run first.
        """
        with self._lock:
            # Use negative priority for max-heap behaviour
            heappush(self._queue, (-task.priority, task))
            self.tasks[task.id] = task

    def get_task(self, task_id: str) -> Task:
        return self.tasks.get(task_id)

    def run_all(self):
        """
        Run all tasks in the queue, in priority order, applying retry policies
        with exponential backoff.
        """
        while True:
            with self._lock:
                if not self._queue:
                    break
                _, task = heappop(self._queue)
            self._execute_task(task)

    def _execute_task(self, task: Task):
        task.state = TaskState.RUNNING
        try:
            # Call the task function
            result = task.func(*task.args, **task.kwargs)
            task.result = result
            task.state = TaskState.SUCCESS
        except Exception as e:
            task.retries_done += 1
            # Check if we can retry
            if task.retry_policy and task.retries_done <= task.retry_policy.max_retries:
                # Exponential backoff: base_delay * 2^(retries_done-1)
                delay = task.retry_policy.retry_delay_seconds * (2 ** (task.retries_done - 1))
                time.sleep(delay)
                return self._execute_task(task)
            else:
                task.state = TaskState.FAILURE
                task.result = e
