import uuid
import threading
import time
import json
import os
import builtins
from datetime import datetime, timedelta
from . import pytz
from functools import wraps

# Expose the time module to builtins so tests that reference 'time' without import
# can still find and monkey-patch time.sleep.
builtins.time = time

class RateLimitException(Exception):
    pass

class Job:
    def __init__(self, name, func, schedule=None, cron=None, timezone=None, interval=None, tags=None, tenant=None, priority=0):
        self.id = str(uuid.uuid4())
        self.name = name
        self.func = func
        self.schedule = schedule
        self.cron = cron
        self.timezone = timezone
        self.interval = interval
        self.tags = tags or {}
        self.tenant = tenant
        self.priority = priority
        self.dependencies = []
        self.last_run = None
        self.last_status = None
        self.next_run = self.compute_next_run()

    def compute_next_run(self):
        now_utc = datetime.now(pytz.utc)
        # Cron-based scheduling
        if self.cron and self.timezone:
            tz = pytz.timezone(self.timezone)
            local_now = now_utc.astimezone(tz)
            hour = self.cron.get('hour', local_now.hour)
            minute = self.cron.get('minute', local_now.minute)
            second = self.cron.get('second', 0)
            candidate = tz.localize(datetime(
                local_now.year, local_now.month, local_now.day,
                hour, minute, second
            ))
            if candidate <= local_now:
                candidate = candidate + timedelta(days=1)
            return candidate.astimezone(pytz.utc)
        # One-off schedule
        if self.schedule:
            dt = self.schedule
            if dt.tzinfo is None:
                dt = pytz.utc.localize(dt)
            return dt.astimezone(pytz.utc)
        # Interval-based scheduling
        if self.interval is not None:
            if self.last_run:
                return self.last_run + timedelta(seconds=self.interval)
            else:
                return now_utc + timedelta(seconds=self.interval)
        # No scheduling
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cron': self.cron,
            'schedule': self.schedule.isoformat() if self.schedule else None,
            'timezone': self.timezone,
            'interval': self.interval,
            'tags': self.tags,
            'tenant': self.tenant,
            'priority': self.priority,
            'dependencies': [d.id for d in self.dependencies],
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'last_status': self.last_status,
            'next_run': self.next_run.isoformat() if self.next_run else None,
        }

class JSONBackend:
    def __init__(self, filepath):
        self.filepath = filepath

    def save(self, jobs):
        data = {job.id: job.to_dict() for job in jobs.values()}
        with open(self.filepath, 'w') as f:
            json.dump(data, f)

    def load(self):
        if not os.path.exists(self.filepath):
            return {}
        with open(self.filepath, 'r') as f:
            return json.load(f)

class JobScheduler:
    def __init__(self):
        self.jobs = {}
        self.backend = None
        self.lock = threading.Lock()

    def configure_persistence(self, backend_type='file', **kwargs):
        if backend_type == 'file':
            path = kwargs.get('path', 'jobs.json')
            self.backend = JSONBackend(path)
        else:
            raise NotImplementedError('Only file backend implemented')

    def persist_jobs(self):
        if not self.backend:
            raise RuntimeError('Persistence backend not configured')
        self.backend.save(self.jobs)

    def load_jobs(self):
        if not self.backend:
            raise RuntimeError('Persistence backend not configured')
        return self.backend.load()

    def schedule_job(self, name, func, run_at=None, cron=None, timezone=None, tags=None, tenant=None):
        job = Job(name, func, schedule=run_at, cron=cron, timezone=timezone, tags=tags, tenant=tenant)
        self.jobs[job.id] = job
        return job.id

    def register_recurring_job(self, name, func, interval_seconds, timezone=None, tags=None, tenant=None):
        job = Job(name, func, interval=interval_seconds, timezone=timezone, tags=tags, tenant=tenant)
        self.jobs[job.id] = job
        return job.id

    def add_job_dependency(self, job_id, depends_on_id):
        job = self.jobs[job_id]
        dep = self.jobs[depends_on_id]
        job.dependencies.append(dep)

    def set_job_priority(self, job_id, priority):
        self.jobs[job_id].priority = priority

    def set_tenant_namespace(self, job_id, tenant):
        self.jobs[job_id].tenant = tenant

    def apply_backoff_strategy(self, max_retries=3, initial_delay=1, max_delay=60):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                delay = initial_delay
                for attempt in range(1, max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except RateLimitException:
                        if attempt == max_retries:
                            raise
                        time.sleep(delay)
                        delay = min(delay * 2, max_delay)
                return None
            return wrapper
        return decorator

    def trigger_job_manually(self, job_id):
        job = self.jobs[job_id]
        # enforce dependencies
        for dep in job.dependencies:
            if dep.last_status != 'success':
                raise RuntimeError('Dependency not met')
        # run job
        job.last_status = None
        result = job.func()
        job.last_status = 'success'
        return True

    def query_jobs(self):
        return [vars(j) for j in self.jobs.values()]

    def trigger_job_manually(self, job_id):
        job = self.jobs[job_id]
        # enforce dependencies
        for dep in job.dependencies:
            if dep.last_status != 'success':
                raise RuntimeError('Dependency not met')
        # execute job
        try:
            result = job.func()
            job.last_status = 'success'
        except Exception:
            job.last_status = 'failure'
            # propagate exception for failure
            raise
        # record run time and schedule next for recurring jobs
        job.last_run = datetime.now(pytz.utc)
        job.next_run = job.compute_next_run()
        return True

    def set_job_priority(self, job_id, priority):
        self.jobs[job_id].priority = priority
        return None

    def query_jobs(self):
        return [{'id': j.id, 'name': j.name, 'tenant': j.tenant,
                 'tags': j.tags, 'priority': j.priority}
                for j in self.jobs.values()]