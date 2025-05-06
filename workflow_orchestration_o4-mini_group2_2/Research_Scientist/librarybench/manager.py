import heapq
import time

from .models import TaskState

class TaskManager:
    def __init__(self):
        self._tasks = {}        # id -> Task
        self._queue = []        # heap of (−priority, counter, task_id)
        self._counter = 0       # tie-breaker for tasks with equal priority

    def add_task(self, task):
        if task.id in self._tasks:
            raise ValueError(f"Task with id {task.id} already exists")
        self._tasks[task.id] = task
        # push on heap with negative priority (so higher priority comes out first)
        heapq.heappush(self._queue, (-task.priority, self._counter, task.id))
        self._counter += 1

    def get_task(self, task_id):
        return self._tasks.get(task_id)

    def run_next(self):
        """
        Pop exactly one task off the queue and run it (if it’s still PENDING).
        Returns the Task or None if there was nothing to run.
        """
        if not self._queue:
            return None

        _, _, tid = heapq.heappop(self._queue)
        task = self._tasks[tid]

        # Skip it if it's already been run or failed
        if task.state != TaskState.PENDING:
            return None

        try:
            res = task.func(*task.args, **task.kwargs)
            task.state = TaskState.SUCCESS
            task.result = res
        except Exception as exc:
            # retry logic
            if task.retries_done < task.retry_policy.max_retries:
                task.retries_done += 1
                time.sleep(task.retry_policy.retry_delay_seconds)
                heapq.heappush(self._queue, (-task.priority, self._counter, task.id))
                self._counter += 1
            else:
                task.state = TaskState.FAILED
                task.error = str(exc)

        return task

    def run_all(self):
        """
        Execute *only* the tasks that were pending at the moment run_all() was called.
        Any tasks added during this run (dynamic children, retries, etc.) stay in the queue
        for the next run_all()/run_next() invocation.
        """
        # Snapshot how many items were pending to start with
        initial_count = len(self._queue)

        for _ in range(initial_count):
            if not self._queue:
                break
            _, _, tid = heapq.heappop(self._queue)
            task = self._tasks[tid]
            if task.state != TaskState.PENDING:
                continue

            try:
                res = task.func(*task.args, **task.kwargs)
                task.state = TaskState.SUCCESS
                task.result = res
            except Exception as exc:
                if task.retries_done < task.retry_policy.max_retries:
                    task.retries_done += 1
                    time.sleep(task.retry_policy.retry_delay_seconds)
                    heapq.heappush(self._queue, (-task.priority, self._counter, task.id))
                    self._counter += 1
                else:
                    task.state = TaskState.FAILED
                    task.error = str(exc)
