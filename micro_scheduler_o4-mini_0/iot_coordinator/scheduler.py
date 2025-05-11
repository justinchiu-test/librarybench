import os
import json
import pickle
import datetime
from zoneinfo import ZoneInfo

class Job:
    def __init__(self, name, tenant, timezone, scheduleexpr, tags=None):
        self.name = name
        self.tenant = tenant
        self.timezone = timezone
        self.scheduleexpr = scheduleexpr
        self.tags = tags or {}
        self.dependencies = []
        self.priority = 0
        self.backoff_strategy = None
        self.backoff_attempts = 0
        self.last_run = None
        self.next_run = None
        self.status = None
        self.recurring = False

    def to_dict(self):
        return {
            'name': self.name,
            'tenant': self.tenant,
            'timezone': self.timezone,
            'scheduleexpr': self.scheduleexpr,
            'tags': self.tags,
            'dependencies': self.dependencies,
            'priority': self.priority,
            'backoff_strategy': self.backoff_strategy,
            'backoff_attempts': self.backoff_attempts,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'status': self.status,
            'recurring': self.recurring
        }

    @classmethod
    def from_dict(cls, data):
        job = cls(
            name=data['name'],
            tenant=data['tenant'],
            timezone=data['timezone'],
            scheduleexpr=data['scheduleexpr'],
            tags=data.get('tags', {})
        )
        job.dependencies = data.get('dependencies', [])
        job.priority = data.get('priority', 0)
        job.backoff_strategy = data.get('backoff_strategy')
        job.backoff_attempts = data.get('backoff_attempts', 0)
        job.last_run = datetime.datetime.fromisoformat(data['last_run']) if data.get('last_run') else None
        job.next_run = datetime.datetime.fromisoformat(data['next_run']) if data.get('next_run') else None
        job.status = data.get('status')
        job.recurring = data.get('recurring', False)
        return job

class FilePersistence:
    def __init__(self, filepath='jobs.pkl', use_json=False):
        self.filepath = filepath
        self.use_json = use_json

    def save(self, data):
        if self.use_json:
            with open(self.filepath, 'w') as f:
                json.dump(data, f)
        else:
            with open(self.filepath, 'wb') as f:
                pickle.dump(data, f)

    def load(self):
        if not os.path.exists(self.filepath):
            return {}
        if self.use_json:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        else:
            with open(self.filepath, 'rb') as f:
                return pickle.load(f)

class RedisPersistence:
    def __init__(self, client, key='jobs'):
        self.client = client
        self.key = key

    def save(self, data):
        blob = pickle.dumps(data)
        self.client.set(self.key, blob)

    def load(self):
        blob = self.client.get(self.key)
        if not blob:
            return {}
        return pickle.loads(blob)

class Scheduler:
    def __init__(self):
        self.jobs = {}  # tenant -> {name: Job}
        self.current_tenant = None
        self.persistence = FilePersistence()

    def set_tenant_namespace(self, tenant):
        self.current_tenant = tenant
        if tenant not in self.jobs:
            self.jobs[tenant] = {}

    def configure_persistence(self, mode, **kwargs):
        if mode == 'file':
            self.persistence = FilePersistence(**kwargs)
        elif mode == 'redis':
            client = kwargs.get('client')
            key = kwargs.get('key', 'jobs')
            self.persistence = RedisPersistence(client, key)
        else:
            raise ValueError("Unknown persistence mode")

    def _get_job(self, name):
        t = self.current_tenant
        if t is None or t not in self.jobs:
            raise KeyError("Tenant not set or no jobs for tenant")
        if name not in self.jobs[t]:
            raise KeyError(f"Job {name} not found")
        return self.jobs[t][name]

    def schedule_job(self, name, timezone, scheduleexpr, tags=None):
        if self.current_tenant is None:
            raise ValueError("Tenant not set")
        job = Job(name, self.current_tenant, timezone, scheduleexpr, tags)
        job.next_run = self._compute_next_run(job)
        self.jobs[self.current_tenant][name] = job
        return job

    def register_recurring_job(self, name, timezone, scheduleexpr, tags=None):
        job = self.schedule_job(name, timezone, scheduleexpr, tags)
        job.recurring = True
        return job

    def _compute_next_run(self, job):
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        tz = ZoneInfo(job.timezone)
        now_local = now_utc.astimezone(tz)
        expr = job.scheduleexpr
        if expr.get('type') == 'daily':
            hour = expr.get('hour', 0)
            minute = expr.get('minute', 0)
            candidate = now_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if candidate <= now_local:
                candidate = candidate + datetime.timedelta(days=1)
            return candidate.astimezone(datetime.timezone.utc)
        elif expr.get('type') == 'weekly':
            weekday = expr.get('weekday', 0)  # Monday=0
            hour = expr.get('hour', 0)
            minute = expr.get('minute', 0)
            days_ahead = (weekday - now_local.weekday() + 7) % 7
            candidate = now_local + datetime.timedelta(days=days_ahead)
            candidate = candidate.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if candidate <= now_local:
                candidate = candidate + datetime.timedelta(days=7)
            return candidate.astimezone(datetime.timezone.utc)
        else:
            # fallback: immediate
            return now_utc

    def trigger_job_manually(self, name):
        job = self._get_job(name)
        now = datetime.datetime.now(datetime.timezone.utc)
        job.last_run = now
        job.status = 'manual'
        if job.recurring:
            old_next = job.next_run
            expr_type = job.scheduleexpr.get('type')
            if expr_type == 'daily':
                job.next_run = old_next + datetime.timedelta(days=1)
            elif expr_type == 'weekly':
                job.next_run = old_next + datetime.timedelta(weeks=1)
            else:
                job.next_run = self._compute_next_run(job)

    def add_job_dependency(self, name, dependency_name):
        job = self._get_job(name)
        job.dependencies.append(dependency_name)

    def query_jobs(self, tenant=None, tags=None, status=None, priority=None):
        t = tenant or self.current_tenant
        if t is None:
            return []
        result = []
        for job in self.jobs.get(t, {}).values():
            if tags and any(job.tags.get(k) != v for k, v in tags.items()):
                continue
            if status and job.status != status:
                continue
            if priority is not None and job.priority != priority:
                continue
            result.append(job)
        # sort by priority desc, then next_run
        result.sort(key=lambda j: (-j.priority,
                                   j.next_run or datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)))
        return result

    def apply_backoff_strategy(self, name, base=1, factor=2, max_backoff=60):
        job = self._get_job(name)
        job.backoff_strategy = {'base': base, 'factor': factor, 'max': max_backoff}
        job.backoff_attempts = 0

    def record_failure(self, name):
        job = self._get_job(name)
        strat = job.backoff_strategy or {'base': 1, 'factor': 2, 'max': 60}
        job.backoff_attempts += 1
        delay = strat['base'] * (strat['factor'] ** (job.backoff_attempts - 1))
        delay = min(delay, strat['max'])
        job.status = 'failed'
        now = datetime.datetime.now(datetime.timezone.utc)
        job.next_run = now + datetime.timedelta(seconds=delay)

    def record_success(self, name):
        job = self._get_job(name)
        job.backoff_attempts = 0
        job.status = 'success'
        if job.recurring:
            job.next_run = self._compute_next_run(job)

    def set_job_priority(self, name, level):
        job = self._get_job(name)
        job.priority = level

    def persist_jobs(self):
        data = {}
        for tenant, jobs in self.jobs.items():
            data[tenant] = {name: job.to_dict() for name, job in jobs.items()}
        self.persistence.save(data)

    def load_jobs(self):
        data = self.persistence.load()
        self.jobs = {}
        for tenant, jobs in data.items():
            self.jobs[tenant] = {}
            for name, jd in jobs.items():
                job = Job.from_dict(jd)
                self.jobs[tenant][name] = job
        # preserve current tenant if exists
        if self.current_tenant and self.current_tenant not in self.jobs:
            self.jobs[self.current_tenant] = {}
