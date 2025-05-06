import time
import threading
from .models import TaskState

class Scheduler:
    """
    Simple scheduler that allows scheduling a Task at fixed intervals.
    """
    def __init__(self):
        self._jobs = []  # list of dicts: {'manager', 'task', 'interval', 'next_run'}
        self._lock = threading.Lock()

    def schedule(self, manager, task, interval_seconds: float):
        """
        Schedule a task to be added to the manager every interval_seconds.
        """
        job = {
            'manager': manager,
            'task': task,
            'interval': interval_seconds,
            'next_run': time.time() + interval_seconds
        }
        with self._lock:
            self._jobs.append(job)

    def run_pending(self):
        """
        Add all due tasks back to their managers. Does not block.
        """
        now = time.time()
        due = []
        with self._lock:
            for job in self._jobs:
                if job['next_run'] <= now:
                    due.append(job)
        for job in due:
            job['manager'].add_task(job['task'])
            job['next_run'] = now + job['interval']
