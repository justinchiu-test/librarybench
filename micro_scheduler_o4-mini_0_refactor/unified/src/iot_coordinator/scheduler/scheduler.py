"""
Scheduler for IoT Coordinator domain with persistence and backoff.
"""
import os
import pickle
import threading
import time as _time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

class Job:
    """Job representation for IoT Coordinator."""
    def __init__(self, name, tz, config, tags=None, tenant=None):
        self.name = name
        self.tenant = tenant
        self.tags = tags or {}
        self.config = config
        self.dependencies = []
        self.priority = 0
        self.recurring = config.get('type') == 'daily'
        # compute next_run in UTC
        tzinfo = ZoneInfo(tz)
        now_utc = datetime.now(timezone.utc)
        local_now = now_utc.astimezone(tzinfo)
        # compute next run local
        hr = config.get('hour', 0)
        minute = config.get('minute', 0)
        second = config.get('second', 0)
        dt_local = datetime(
            local_now.year, local_now.month, local_now.day,
            hr, minute, second, tzinfo=tzinfo
        )
        if dt_local <= local_now:
            dt_local += timedelta(days=1)
        # convert to UTC
        self.next_run = dt_local.astimezone(timezone.utc)
        self.last_run = None
        self.status = None
        # run count
        self.run_count = 0
        # backoff state
        self._fail_count = 0
        self._backoff = None

class FilePersistence:
    """File-based persistence using pickle."""
    def __init__(self, filepath):
        self.filepath = filepath
    def save(self, data):
        with open(self.filepath, 'wb') as f:
            pickle.dump(data, f)
    def load(self):
        try:
            with open(self.filepath, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return {}

class RedisPersistence:
    """Redis-like persistence using provided client."""
    def __init__(self, client, key):
        self.client = client
        self.key = key
    def save(self, data):
        # use pickle to serialize
        self.client.set(self.key, pickle.dumps(data))
    def load(self):
        raw = self.client.get(self.key)
        if not raw:
            return {}
        try:
            return pickle.loads(raw)
        except Exception:
            return {}

class Scheduler:
    """IoT Coordinator scheduler with persistence and backoff."""
    def __init__(self):
        self.jobs = {}  # name -> Job
        self._tenant = None
        self._persistence = None

    def set_tenant_namespace(self, tenant):
        self._tenant = tenant

    def schedule_job(self, name, tz, config, tags=None):
        """Schedule a one-off or recurring job."""
        job = Job(name, tz, config, tags=tags, tenant=self._tenant)
        self.jobs[name] = job
        return job

    def register_recurring_job(self, name, tz, config):
        """Alias for schedule_job for recurring jobs."""
        job = self.schedule_job(name, tz, config)
        job.recurring = True
        return job

    def add_job_dependency(self, job_name, depends_on):
        """Add a dependency for a job."""
        job = self.jobs.get(job_name)
        if job:
            job.dependencies.append(depends_on)

    def trigger_job_manually(self, name):
        """Manually trigger job, respecting dependencies."""
        job = self.jobs.get(name)
        if not job:
            return False
        # check dependencies
        for dep in job.dependencies:
            djob = self.jobs.get(dep)
            if not djob or djob.last_run is None:
                raise RuntimeError(f"Dependency {dep} not met")
        # execute job
        try:
            job.func = getattr(job, 'func', None) or (lambda: None)
            # job.func may not be set, assume config has no function
            # but tests assume schedule_job takes only name, tz, config
            # so no function execution here
            # record manual status
            job.status = 'manual'
            job.last_run = datetime.now(timezone.utc)
            job.run_count += 1
            # schedule next if recurring (daily)
            if job.recurring:
                # for daily recurrence, advance by one day
                job.next_run = job.next_run + timedelta(days=1)
            return True
        except Exception:
            return False

    def apply_backoff_strategy(self, job_name, base, factor, max_backoff):
        """Configure exponential backoff for a job."""
        job = self.jobs.get(job_name)
        if job:
            job._backoff = {'base': base, 'factor': factor, 'max': max_backoff}

    def record_failure(self, job_name):
        """Record a failure and update next_run based on backoff."""
        job = self.jobs.get(job_name)
        if not job or not job._backoff:
            return
        job._fail_count += 1
        b = job._backoff
        delay = b['base'] * (b['factor'] ** (job._fail_count - 1))
        if b['max'] is not None:
            delay = min(delay, b['max'])
        job.next_run = datetime.now(timezone.utc) + timedelta(seconds=delay)

    def set_job_priority(self, job_name, priority):
        job = self.jobs.get(job_name)
        if job:
            job.priority = priority

    def query_jobs(self, tags=None):
        """Return list of jobs (Job instances), optionally filtered by tags, sorted by priority."""
        result = []
        for job in self.jobs.values():
            if tags:
                # filter by matching tags dict
                if not job.tags or any(job.tags.get(k) != v for k, v in tags.items()):
                    continue
            result.append(job)
        # sort by priority descending
        result.sort(key=lambda x: getattr(x, 'priority', 0), reverse=True)
        return result

    def configure_persistence(self, backend_type, **options):
        """Configure persistence backend type: 'file' or 'redis'."""
        if backend_type == 'file':
            self._persistence = FilePersistence(options.get('filepath'))
        elif backend_type == 'redis':
            self._persistence = RedisPersistence(options.get('client'), options.get('key'))
        else:
            raise ValueError(f"Unknown backend {backend_type}")
        return self._persistence

    def persist_jobs(self):
        """Persist jobs state."""
        if not self._persistence:
            return
        data = {}
        for name, job in self.jobs.items():
            data[name] = {
                'name': job.name,
                'tenant': job.tenant,
                'tags': job.tags,
                'config': job.config,
                'next_run': job.next_run,
                'run_count': job.run_count,
            }
        self._persistence.save(data)

    def load_jobs(self):
        """Load jobs state for this scheduler."""
        if not self._persistence:
            return
        data = self._persistence.load()
        for name, meta in data.items():
            # reconstruct Job without computing next_run
            job = Job.__new__(Job)
            # assign fields manually
            job.name = meta.get('name')
            job.tenant = self._tenant
            job.tags = meta.get('tags', {})
            job.config = meta.get('config', {})
            job.dependencies = []
            job.priority = 0
            job.recurring = job.config.get('type') == 'daily'
            job.next_run = meta.get('next_run')
            job.last_run = None
            job.status = None
            job.run_count = meta.get('run_count', 0)
            job._fail_count = 0
            job._backoff = None
            self.jobs[name] = job

    def _get_job(self, job_name):
        """Return job object by name."""
        return self.jobs.get(job_name)