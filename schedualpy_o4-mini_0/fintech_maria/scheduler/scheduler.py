import threading
import time
import uuid
from datetime import datetime
from scheduler.utils import apply_jitter_and_drift_correction, calculate_drift
from scheduler.metrics import MetricsExporter
from scheduler.hooks import apply_hooks

class ThreadSafeScheduler:
    def __init__(self):
        self._jobs = {}
        self._lock = threading.Lock()
        self.metrics = MetricsExporter()

    def schedule_one_off_task(self, func, run_at):
        """
        Schedule func to run once at a datetime or timestamp in seconds.
        """
        if isinstance(run_at, (int, float)):
            delay = max(0, run_at - time.time())
        else:
            delay = max(0, (run_at - datetime.now(run_at.tzinfo)).total_seconds())
        job_id = str(uuid.uuid4())
        # Store the function and timer
        timer = threading.Timer(delay, self._run_job, args=(job_id, func, None, datetime.now()))
        with self._lock:
            self._jobs[job_id] = {'timer': timer, 'interval': None, 'func': func}
        timer.start()
        return job_id

    def schedule_recurring(self, func, interval, sla_jitter=0):
        """
        Schedule func to run every 'interval' seconds with optional jitter.
        """
        job_id = str(uuid.uuid4())
        next_run = time.time() + apply_jitter_and_drift_correction(interval, sla_jitter)

        def _recurring(previous_expected):
            expected = previous_expected + interval
            actual = time.time()
            drift = calculate_drift(datetime.fromtimestamp(previous_expected),
                                    datetime.fromtimestamp(actual))
            self.metrics.observe_histogram('job_drift_seconds', drift)
            self.metrics.inc_counter('job_runs')
            self._run_job(job_id, func, expected, previous_expected)
            # Schedule next run
            with self._lock:
                if job_id in self._jobs:
                    t = threading.Timer(interval, _recurring, args=(expected,))
                    self._jobs[job_id]['timer'] = t
                    t.start()

        timer = threading.Timer(next_run - time.time(), _recurring, args=(next_run - interval,))
        with self._lock:
            self._jobs[job_id] = {'timer': timer, 'interval': interval, 'func': func}
        timer.start()
        return job_id

    def dynamic_reschedule(self, job_id, new_interval):
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                raise KeyError(f"No job {job_id}")
            # Cancel existing timer
            job['timer'].cancel()
            job['interval'] = new_interval
            func = job.get('func')

        def _resched():
            self._run_job(job_id, func, time.time(), None)
            with self._lock:
                if job_id in self._jobs:
                    t = threading.Timer(new_interval, _resched)
                    self._jobs[job_id]['timer'] = t
                    t.start()

        t = threading.Timer(new_interval, _resched)
        with self._lock:
            self._jobs[job_id]['timer'] = t
        t.start()

    def cancel(self, job_id):
        with self._lock:
            job = self._jobs.pop(job_id, None)
        if job and job.get('timer'):
            job['timer'].cancel()

    def _run_job(self, job_id, func, expected_time, previous_expected):
        """
        Internal runner applying hooks and metrics.
        """
        start = time.time()
        try:
            wrapped = apply_hooks(func)
            wrapped()
            self.metrics.inc_counter('job_success')
        except Exception:
            self.metrics.inc_counter('job_failure')
        duration = time.time() - start
        self.metrics.observe_histogram('job_duration_seconds', duration)

        # Clean up one-off jobs
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.get('interval') is None:
                self._jobs.pop(job_id, None)

    def list_jobs(self):
        with self._lock:
            return list(self._jobs.keys())
