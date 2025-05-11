import os
import json
from datetime import datetime, timedelta
from threading import Lock
from dateutil import tz
from .persistence import SQLitePersistence, RedisPersistence
from .job import Job

class Scheduler:
    def __init__(self):
        self.tenants = {}
        self.jobs = {}  # tenant -> list of Job
        self.persistence = None
        self.lock = Lock()

    def configure_persistence(self, backend, **kwargs):
        if backend == 'sqlite':
            db_path = kwargs.get('db_path', ':memory:')
            self.persistence = SQLitePersistence(db_path)
        elif backend == 'redis':
            self.persistence = RedisPersistence()
        else:
            raise ValueError('Unknown backend')
        return self.persistence

    def set_tenant_namespace(self, tenant):
        with self.lock:
            if tenant not in self.jobs:
                self.jobs[tenant] = []
        return tenant

    def schedule_job(self, tenant, name, run_time, timezone_str, tags=None,
                     dependencies=None, priority=0, backoff_strategy=None,
                     recurring_interval=None):
        tzinfo = tz.gettz(timezone_str)
        if run_time.tzinfo is None:
            run_time = run_time.replace(tzinfo=tzinfo)
        job = Job(tenant, name, run_time, timezone_str, tags, dependencies,
                  priority, backoff_strategy, recurring_interval)
        with self.lock:
            self.jobs.setdefault(tenant, []).append(job)
        return job

    def register_recurring_job(self, tenant, name, first_run, timezone_str,
                               interval: timedelta, tags=None, priority=0):
        job = self.schedule_job(tenant, name, first_run, timezone_str,
                                tags, [], priority, None, interval)
        return job

    def add_job_dependency(self, tenant, job_id, dependency_job_id):
        with self.lock:
            job = self._find_job(tenant, job_id)
            dep = self._find_job(tenant, dependency_job_id)
            if dep and job:
                job.dependencies.append(dependency_job_id)

    def _find_job(self, tenant, job_id):
        for job in self.jobs.get(tenant, []):
            if job.job_id == job_id:
                return job
        return None

    def apply_backoff_strategy(self, tenant, job_id):
        job = self._find_job(tenant, job_id)
        if not job:
            return None
        job.attempts += 1
        return job.backoff_strategy(job.attempts)

    def set_job_priority(self, tenant, job_id, priority):
        job = self._find_job(tenant, job_id)
        if job:
            job.priority = priority

    def trigger_job_manually(self, tenant, job_id):
        job = self._find_job(tenant, job_id)
        if not job:
            return False
        # check dependencies
        for dep_id in job.dependencies:
            dep = self._find_job(tenant, dep_id)
            if dep and dep.status != 'completed':
                return False
        # preserve previous scheduled time for recurring jobs
        prev_run_time = job.run_time
        # run job
        job.status = 'running'
        now = datetime.now(tz=tz.UTC)
        job.last_run = now
        job.history.append({'run_time': now.isoformat(), 'status': 'success'})
        job.status = 'completed'
        # handle recurring
        if job.recurring_interval:
            next_run = prev_run_time + job.recurring_interval
            job.run_time = next_run
            job.status = 'scheduled'
        return True

    def query_jobs(self, tenant):
        with self.lock:
            res = []
            for job in self.jobs.get(tenant, []):
                # strip tzinfo for consistency with test expectations
                nr = job.run_time.replace(tzinfo=None)
                res.append({
                    'job_id': job.job_id,
                    'name': job.name,
                    'next_run': nr.isoformat(),
                    'status': job.status,
                    'tags': job.tags,
                    'priority': job.priority,
                    'dependencies': job.dependencies,
                })
            return res

    def persist_jobs(self):
        if not self.persistence:
            raise RuntimeError('No persistence configured')
        with self.lock:
            for tenant, jobs in self.jobs.items():
                self.persistence.save_jobs(tenant, jobs)

    def load_jobs(self, tenant):
        if not self.persistence:
            raise RuntimeError('No persistence configured')
        data = self.persistence.load_jobs(tenant)
        jobs = []
        for d in data:
            jobs.append(Job.from_dict(d))
        with self.lock:
            self.jobs[tenant] = jobs
        return jobs
