import time
import heapq
from threading import Lock
from pipeline.tasks import TaskState

class SchedulerError(Exception):
    """Exception raised for scheduler authorization errors."""
    pass

class Scheduler:
    """
    Scheduler for managing and running tasks.
    Uses a priority queue ordered by next_run_time and task priority.
    Supports dynamic task creation and retry mechanisms.
    """
    def __init__(self, auth):
        """
        auth: an Auth instance for authorization checks
        """
        self._auth = auth
        self._queue = []       # heap of (run_time, -priority, counter, Task)
        self._lock = Lock()
        self._counter = 0
        self.tasks = {}        # name -> Task

    def add_task(self, task, token):
        """
        Add a task to the schedule. Requires 'add_task' permission.
        """
        if not self._auth.authorize(token, 'add_task'):
            raise SchedulerError("Unauthorized to add tasks")
        with self._lock:
            self._counter += 1
            entry = (task.next_run_time, -task.priority, self._counter, task)
            heapq.heappush(self._queue, entry)
            self.tasks[task.name] = task

    def run_pending(self, token):
        """
        Run all tasks whose next_run_time <= now.
        Handles retries, backoff, and dynamic task creation.
        Requires 'run_scheduler' permission.
        """
        if not self._auth.authorize(token, 'run_scheduler'):
            raise SchedulerError("Unauthorized to run scheduler")
        now = time.time()
        new_tasks = []
        with self._lock:
            # Pop and execute ready tasks
            while self._queue and self._queue[0][0] <= now:
                _, _, _, task = heapq.heappop(self._queue)
                result = task.run()
                # Handle dynamic tasks
                if result:
                    if isinstance(result, list):
                        new_tasks.extend(result)
                # Re-queue if still pending (for retries)
                if task.state == TaskState.PENDING:
                    self._counter += 1
                    entry = (task.next_run_time, -task.priority, self._counter, task)
                    heapq.heappush(self._queue, entry)
            # Add any dynamically created tasks
            for t in new_tasks:
                self.add_task(t, token)
