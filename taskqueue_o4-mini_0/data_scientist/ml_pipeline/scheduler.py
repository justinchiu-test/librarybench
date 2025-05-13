import threading
import uuid
from datetime import datetime

class Scheduler:
    def __init__(self):
        self.jobs = {}

    def schedule(self, run_time, func, *args, **kwargs):
        if isinstance(run_time, (int, float)):
            delay = run_time
        elif isinstance(run_time, datetime):
            delay = (run_time - datetime.now()).total_seconds()
        else:
            raise TypeError("run_time must be datetime or seconds")
        if delay < 0:
            delay = 0
        timer = threading.Timer(delay, func, args=args, kwargs=kwargs)
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = timer
        timer.daemon = True
        timer.start()
        return job_id

    def cancel(self, job_id):
        timer = self.jobs.get(job_id)
        if timer:
            timer.cancel()
            del self.jobs[job_id]
            return True
        return False
