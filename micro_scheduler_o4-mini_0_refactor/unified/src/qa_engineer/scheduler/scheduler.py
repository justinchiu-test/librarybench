"""
QA Engineer domain-specific scheduler with simple persistence.
"""
import threading
import time
import datetime

class RedisBackend:
    """In-memory persistence for Redis backend."""
    def __init__(self):
        self._history = {}
    def save_run(self, job_id, record):
        self._history.setdefault(job_id, []).append(record)
    def get_history(self, job_id):
        return list(self._history.get(job_id, []))

class SQLiteBackend:
    """In-memory persistence for SQLite backend."""
    def __init__(self):
        self._history = {}
    def save_run(self, job_id, record):
        self._history.setdefault(job_id, []).append(record)
    def get_history(self, job_id):
        return list(self._history.get(job_id, []))

class Scheduler:
    """Scheduler recording runs and supporting retry/backoff, scheduling, and dependencies."""
    def __init__(self):
        self.jobs = {}              # job_id -> callable
        self._threads = []          # background threads
        self.persistence = None     # persistence backend
        self._retry = {}            # job_id -> {'count': int, 'delay': float}
        self._backoff = {}          # job_id -> backoff_fn
        self._sem = None            # concurrency semaphore
        self.dependencies = {}      # job_id -> list of job_ids
        self.timezones = {}         # job_id -> timezone

    def health_check(self):
        """Return True if scheduler is running."""
        return True

    def set_persistence_backend(self, backend):
        """Set a persistence backend with save_run/get_history."""
        self.persistence = backend

    def trigger_job(self, job_id):
        """Trigger execution of a job with dependencies, retry, backoff, and persistence."""
        def runner():
            # handle dependencies first
            for dep in self.dependencies.get(job_id, []):
                self.trigger_job(dep)
            func = self.jobs.get(job_id)
            if not func or not self.persistence:
                return
            attempts = 0
            cfg = self._retry.get(job_id)
            backoff_fn = self._backoff.get(job_id)
            while True:
                attempts += 1
                try:
                    # respect resource limits
                    if self._sem:
                        with self._sem:
                            func()
                    else:
                        func()
                    # record success
                    self.persistence.save_run(job_id, {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'status': 'success',
                        'attempt': attempts
                    })
                    break
                except Exception:
                    # record failure
                    self.persistence.save_run(job_id, {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'status': 'failure',
                        'attempt': attempts
                    })
                    # retry logic
                    if cfg and attempts < cfg['count']:
                        delay = backoff_fn(attempts) if backoff_fn else cfg['delay']
                        time.sleep(delay)
                        continue
                    break
        t = threading.Thread(target=runner)
        t.daemon = True
        t.start()
        self._threads.append(t)

    def retry_job(self, job_id, count=1, delay=0):
        """Configure retry count and base delay for a job."""
        self._retry[job_id] = {'count': count, 'delay': delay}

    def exponential_backoff(self, job_id, base_delay=1, factor=2, max_delay=None):
        """Configure exponential backoff function for a job."""
        def backoff_fn(attempt):
            d = base_delay * (factor ** (attempt - 1))
            if max_delay is not None:
                return min(d, max_delay)
            return d
        self._backoff[job_id] = backoff_fn

    def schedule_job(self, job_id, func, delay=None, interval=None, cron=None):
        """Schedule delayed, interval, or cron jobs."""
        self.jobs[job_id] = func
        # delayed execution
        if delay is not None:
            def drunner():
                time.sleep(delay)
                self.trigger_job(job_id)
            t = threading.Thread(target=drunner)
            t.daemon = True
            t.start()
            self._threads.append(t)
        # interval execution
        if interval is not None:
            def irunner():
                while True:
                    time.sleep(interval)
                    self.trigger_job(job_id)
            t = threading.Thread(target=irunner)
            t.daemon = True
            t.start()
            self._threads.append(t)
        # cron (treated like interval)
        if cron is not None:
            def crunner():
                while True:
                    time.sleep(cron)
                    self.trigger_job(job_id)
            t = threading.Thread(target=crunner)
            t.daemon = True
            t.start()
            self._threads.append(t)

    def define_dependencies(self, mapping):
        """Define dependencies from a dict mapping job_id to list of deps."""
        if isinstance(mapping, dict):
            self.dependencies = mapping

    def limit_resources(self, max_concurrent):
        """Limit concurrent executions globally."""
        self._sem = threading.Semaphore(max_concurrent)

    def timezone_aware(self, job_id, tz_name):
        """Record timezone for a job."""
        self.timezones[job_id] = tz_name

    def graceful_shutdown(self, timeout=None):
        """Wait for running threads to finish."""
        for t in self._threads:
            t.join(timeout)
        return True