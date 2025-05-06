import threading
import time
import datetime
from queue import Queue, Empty
from typing import Callable, Optional, Tuple, Any
from .tasks import Task
from .alert import AlertManager
from utils import get_due_jobs

class ScheduledJob:
    def __init__(
        self,
        task_callable: Callable,
        args: Tuple[Any, ...],
        kwargs: dict,
        run_at: Optional[datetime.datetime] = None,
        interval: Optional[float] = None,
    ):
        self.task_callable = task_callable
        self.args = args
        self.kwargs = kwargs or {}
        self.run_at = run_at or datetime.datetime.utcnow()
        self.interval = interval  # seconds

    def next_run(self):
        return self.run_at

    def reschedule(self):
        if self.interval:
            self.run_at = self.run_at + datetime.timedelta(seconds=self.interval)

class Scheduler:
    """
    Simple scheduler with queue and worker thread.
    """
    def __init__(self):
        self._jobs: list[ScheduledJob] = []
        self._queue = Queue()
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._running = False

    def start(self):
        self._running = True
        if not self._worker.is_alive():
            self._worker = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker.start()

    def stop(self):
        self._running = False

    def schedule(
        self, 
        task: Task, 
        args: Tuple = (), 
        kwargs: dict = None, 
        run_at: Optional[datetime.datetime] = None, 
        interval: Optional[float] = None
    ):
        job = ScheduledJob(task.run, args, kwargs, run_at, interval)
        self._jobs.append(job)

    def _worker_loop(self):
        while self._running:
            now = datetime.datetime.utcnow()
            due = get_due_jobs(self._jobs, now)
            for job in due:
                self._queue.put((job.task_callable, job.args, job.kwargs, job))
                if job.interval:
                    job.reschedule()
                else:
                    self._jobs.remove(job)
            try:
                func, args, kwargs, job = self._queue.get(timeout=0.1)
            except Empty:
                time.sleep(0.1)
                continue
            try:
                func(*args, **kwargs)
            except Exception as e:
                AlertManager.send_message("scheduler", f"Job failed: {e}")
            finally:
                self._queue.task_done()

    def run_pending(self):
        """
        For testing: manually run due jobs without threading.
        """
        now = datetime.datetime.utcnow()
        due = get_due_jobs(self._jobs, now)
        for job in due:
            try:
                job.task_callable(*job.args, **job.kwargs)
            except Exception as e:
                AlertManager.send_message("scheduler", f"Job failed: {e}")
            if job.interval:
                job.reschedule()
            else:
                self._jobs.remove(job)
