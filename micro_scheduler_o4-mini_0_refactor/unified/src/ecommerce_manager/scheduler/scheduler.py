import time
import os
from datetime import datetime, timedelta, timezone

import ecommerce_manager.pytz as pytz
from scheduler.persistence.file import FileBackend

class RateLimitException(Exception):
    """Exception to signal rate limiting for backoff."""
    pass

class Job:
    """Internal job representation."""
    def __init__(self, job_id, name, func, run_at=None, interval_seconds=None,
                 cron=None, timezone_str=None, tags=None, tenant=None):
        self.job_id = job_id
        self.name = name
        self.func = func
        self.run_at = run_at
        self.interval = interval_seconds
        self.cron = cron
        self.timezone = timezone_str
        self.tags = tags
        self.tenant = tenant
        self.dependencies = []
        self.next_run = None
        self.last_run = None
        self.recurring = False
        self.priority = 0
        # compute initial next_run
        if interval_seconds is not None:
            self.recurring = True
            # initial next run from now in UTC
            self.next_run = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=interval_seconds)
        elif run_at is not None:
            # one-off schedule
            self.next_run = run_at
        elif cron is not None and timezone_str is not None:
            tz = pytz.timezone(timezone_str)
            now_utc = datetime.now(pytz.utc)
            local_now = now_utc.astimezone(tz)
            # build target local datetime
            dt_local = tz.localize(datetime(
                local_now.year, local_now.month, local_now.day,
                cron.get('hour', 0), cron.get('minute', 0), cron.get('second', 0)
            ))
            if dt_local <= local_now:
                dt_local = dt_local + timedelta(days=1)
            self.next_run = dt_local.astimezone(pytz.utc)
        else:
            # default immediate
            self.next_run = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.run_count = 0

class JobScheduler:
    """Scheduler for eCommerce Manager domain."""
    def __init__(self):
        self.jobs = {}  # job_id -> Job
        self.persistence = None

    def register_recurring_job(self, name, func, interval_seconds):
        job_id = name
        job = Job(job_id, name, func, interval_seconds=interval_seconds)
        self.jobs[job_id] = job
        return job_id

    def schedule_job(self, name, func, run_at=None, cron=None, timezone=None,
                     tags=None, tenant=None):
        job_id = name
        job = Job(job_id, name, func, run_at=run_at,
                  interval_seconds=None, cron=cron, timezone_str=timezone,
                  tags=tags, tenant=tenant)
        self.jobs[job_id] = job
        return job_id

    def add_job_dependency(self, job_id, depends_on):
        job = self.jobs.get(job_id)
        if job:
            job.dependencies.append(depends_on)

    def trigger_job_manually(self, job_id):
        job = self.jobs.get(job_id)
        if not job:
            return False
        # ensure dependencies
        for dep in job.dependencies:
            djob = self.jobs.get(dep)
            if not djob or djob.last_run is None:
                raise RuntimeError(f"Dependency {dep} not run yet")
        # run job
        try:
            job.func()
            job.last_run = datetime.utcnow().replace(tzinfo=timezone.utc)
            job.run_count += 1
            # update next_run for recurring jobs
            if job.recurring:
                job.next_run = job.last_run + timedelta(seconds=job.interval)
            return True
        except Exception:
            return False

    def configure_persistence(self, backend_type, **options):
        if backend_type == 'file':
            path = options.get('path')
            self.persistence = FileBackend(path)
        else:
            raise ValueError(f"Unknown backend {backend_type}")
        return self.persistence

    def persist_jobs(self):
        if not self.persistence:
            return
        data = {}
        for jid, job in self.jobs.items():
            data[jid] = {
                'name': job.name,
                'run_count': job.run_count,
            }
        self.persistence.save(data)

    def load_jobs(self):
        if not self.persistence:
            return {}
        return self.persistence.load()

    def query_jobs(self, tags=None):
        result = []
        for job in self.jobs.values():
            if tags and job.tags != tags:
                continue
            result.append({
                'id': job.job_id,
                'name': job.name,
                'tags': job.tags,
                'tenant': job.tenant,
                'next_run': job.next_run,
                'priority': job.priority,
            })
        result.sort(key=lambda x: x['priority'], reverse=True)
        return result

    def set_job_priority(self, job_id, priority):
        job = self.jobs.get(job_id)
        if job:
            job.priority = priority

    def apply_backoff_strategy(self, max_retries, initial_delay, max_delay):
        def decorator(fn):
            def wrapper(*args, **kwargs):
                retries = 0
                delay = initial_delay
                while True:
                    try:
                        return fn(*args, **kwargs)
                    except RateLimitException:
                        retries += 1
                        if retries > max_retries:
                            raise
                        time.sleep(delay)
                        delay = min(delay * 2, max_delay)
            return wrapper
        return decorator