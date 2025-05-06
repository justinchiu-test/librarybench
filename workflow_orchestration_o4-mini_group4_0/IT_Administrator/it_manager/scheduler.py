import threading
import time
import datetime
from queue import Queue, Empty
from typing import Tuple, Any, Optional
from .tasks import Task
from .alert import AlertManager
from utils import execute_job

class ScheduledJob:
    def __init__(
        self,
        task_callable,
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
        self._jobs = []
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
        job = ScheduledJob(task.run, args, kwargs or {}, run_at, interval)
        self._jobs.append(job)

    def _worker_loop(self):
        while self._running:
            now = datetime.datetime.utcnow()
            # enqueue due jobs
            for job in list(self._jobs):
                if job.next_run() <= now:
                    self._queue.put((job,))
                    if job.interval:
                        job.reschedule()
                    else:
                        self._jobs.remove(job)
            # process one job from the queue
            try:
                (job,) = self._queue.get(timeout=0.1)
            except Empty:
                time.sleep(0.1)
                continue
            execute_job(job.task_callable, job.args, job.kwargs, alert_channel="scheduler")
            self._queue.task_done()

    def run_pending(self):
        """
        For testing: manually run due jobs without threading.
        """
        now = datetime.datetime.utcnow()
        due = [j for j in self._jobs if j.next_run() <= now]
        for job in due:
            execute_job(job.task_callable, job.args, job.kwargs, alert_channel="scheduler")
            if job.interval:
                job.reschedule()
            else:
                self._jobs.remove(job)
