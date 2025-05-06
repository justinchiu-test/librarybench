import time
from models import TaskState

class TaskManager:
    def __init__(self):
        self.tasks = {}

    def add_task(self, task):
        """
        Add a Task. If a task with the same id already exists, raises ValueError.
        """
        if task.id in self.tasks:
            raise ValueError(f"Task with id {task.id} already exists")
        self.tasks[task.id] = task

    def get_task(self, task_id):
        """
        Retrieve a Task by id, or None if not found.
        """
        return self.tasks.get(task_id)

    def run_all(self):
        """
        Run through all tasks that were pending at the time run_all() was invoked,
        in priority order, respecting retry policies.  Any tasks added dynamically
        during this run will remain pending and only be picked up on a subsequent
        run_all() call.
        """
        # Snapshot the tasks (id -> Task) as they exist right now
        snapshot_tasks = dict(self.tasks)

        # Continue until there are no more pending tasks in the snapshot
        while True:
            # Find pending tasks from the snapshot
            pending = [t for t in snapshot_tasks.values()
                       if t.state == TaskState.PENDING]

            if not pending:
                # No more pending tasks from the original snapshot
                break

            # Pick the highest-priority task (ties broken arbitrarily)
            next_task = max(pending, key=lambda t: t.priority)
            next_task.state = TaskState.RUNNING

            try:
                # Execute the task
                result = next_task.func(*next_task.args, **next_task.kwargs)
            except Exception:
                # On exception, handle retry or mark as failed
                next_task.retries_done += 1
                if next_task.retries_done <= next_task.retry_policy.max_retries:
                    # Delay before retrying (tests may monkeypatch time.sleep to no-op)
                    time.sleep(next_task.retry_policy.retry_delay_seconds)
                    next_task.state = TaskState.PENDING
                else:
                    next_task.state = TaskState.FAILED
            else:
                # Success path
                next_task.state = TaskState.SUCCESS
                next_task.result = result
