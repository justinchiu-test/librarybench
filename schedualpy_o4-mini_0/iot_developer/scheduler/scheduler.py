import datetime
import random

class Scheduler:
    def __init__(self):
        self._jobs = {}

    def schedule(self, job_id, func, cron_interval_seconds, jitter_seconds=0, recurring=False):
        self._jobs[job_id] = {
            'func': func,
            'interval': cron_interval_seconds,
            'jitter': jitter_seconds,
            'recurring': recurring
        }

    def next_run(self, job_id, last_run=None):
        job = self._jobs.get(job_id)
        if not job:
            raise KeyError(f"No such job: {job_id}")
        base = last_run or datetime.datetime.utcnow()
        interval = job['interval']
        jitter = job['jitter']
        delta = interval + (random.uniform(0, jitter) if jitter else 0)
        return base + datetime.timedelta(seconds=delta)
