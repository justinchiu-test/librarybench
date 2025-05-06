import threading
from core.logger import logger
from utils import create_daemon_thread, schedule_interval_job

class Scheduler:
    def __init__(self):
        self._jobs = []
        self._stop = False

    def schedule_workflow(self, workflow, interval_seconds):
        stop_check = lambda: self._stop
        job = lambda: schedule_interval_job(workflow, interval_seconds, stop_check, logger)
        t = create_daemon_thread(job)
        self._jobs.append(t)

    def stop_all(self):
        self._stop = True
        for t in self._jobs:
            if t.is_alive():
                t.join(timeout=1)
