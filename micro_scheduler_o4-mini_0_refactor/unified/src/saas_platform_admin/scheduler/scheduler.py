import os
import json
from datetime import datetime, timedelta, timezone

class SQLiteBackend:
    """Simple file-based persistence using JSON."""
    def __init__(self, db_path):
        self.db_path = db_path
    def save(self, data):
        # data is a dict mapping tenants to job records
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, default=str)
        except Exception:
            pass
    def load(self):
        try:
            with open(self.db_path) as f:
                return json.load(f)
        except Exception:
            return {}

class RedisBackend:
    """In-memory persistence backend."""
    def __init__(self):
        self.store = {}
    def save(self, data):
        # simply store as a JSON-serializable
        self.store.clear()
        self.store.update(data)
    def load(self):
        return dict(self.store)

class Job:
    """Job representation for SaaS Platform Admin."""
    def __init__(self, tenant, job_id, name, run_time, timezone_str, tags=None):
        self.tenant = tenant
        self.job_id = job_id
        self.name = name
        self.run_time = run_time
        self.timezone = timezone_str
        self.tags = tags or {}
        self.dependencies = []
        self.backoff_strategy = None
        self.priority = 0
        self.interval = None
        self.recurring = False
        self.last_run = None

class Scheduler:
    """SaaS Platform Admin Scheduler."""
    def __init__(self):
        self._persistence = None
        self._tenant = None
        self._jobs = {}  # job_id -> Job

    def configure_persistence(self, backend_type, **options):
        """Configure persistence backend: 'sqlite' or 'redis'."""
        if backend_type == 'sqlite':
            self._persistence = SQLiteBackend(options.get('db_path'))
        elif backend_type == 'redis':
            self._persistence = RedisBackend()
        else:
            raise ValueError(f"Unknown backend {backend_type}")
        return self._persistence

    def set_tenant_namespace(self, tenant):
        self._tenant = tenant

    def schedule_job(self, tenant, job_id, run_time, timezone_str, tags=None, backoff_strategy=None):
        """Schedule a one-off job."""
        # attach timezone info
        dt = run_time
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        job = Job(tenant, job_id, job_id, dt, timezone_str, tags=tags)
        job.backoff_strategy = backoff_strategy
        self._jobs[job_id] = job
        return job

    def add_job_dependency(self, tenant, job_id, dep_job_id):
        job = self._jobs.get(job_id)
        if job and job.tenant == tenant:
            job.dependencies.append(dep_job_id)

    def apply_backoff_strategy(self, tenant, job_id):
        """Apply backoff strategy for job and return delay."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        # count attribute
        count = getattr(job, '_backoff_count', 0) + 1
        job._backoff_count = count
        if job.backoff_strategy:
            return job.backoff_strategy(count)
        # default exponential: base=1, factor=2
        return 2 ** count

    def set_job_priority(self, tenant, job_id, priority):
        job = self._jobs.get(job_id)
        if job and job.tenant == tenant:
            job.priority = priority

    def register_recurring_job(self, tenant, job_id, first_run, timezone_str, interval):
        """Register a recurring job with initial run and interval."""
        job = self.schedule_job(tenant, job_id, first_run, timezone_str)
        job.recurring = True
        job.interval = interval
        return job

    def trigger_job_manually(self, tenant, job_id):
        """Manually trigger a job; enforce dependencies for tenant."""
        job = self._jobs.get(job_id)
        if not job or job.tenant != tenant:
            return False
        for dep in job.dependencies:
            djob = self._jobs.get(dep)
            if not djob or djob.last_run is None:
                return False
        # run job
        try:
            job.last_run = datetime.now(timezone.utc)
            job.status = 'manual'
            if job.recurring:
                job.run_time = job.run_time + job.interval
            return True
        except Exception:
            return False

    def query_jobs(self, tenant, tags=None):
        """Return list of job dicts for tenant, filtered and sorted by priority."""
        out = []
        for job in self._jobs.values():
            if job.tenant != tenant:
                continue
            if tags:
                # tags is dict of filters
                if any(job.tags.get(k) != v for k, v in tags.items()):
                    continue
            # format next_run as naive ISO string
            nr = job.run_time
            # convert to UTC and drop tzinfo
            if hasattr(nr, 'tzinfo') and nr.tzinfo is not None:
                nr = nr.astimezone(timezone.utc).replace(tzinfo=None)
            next_run_str = nr.isoformat()
            out.append({
                'tenant': job.tenant,
                'job_id': job.job_id,
                'name': job.name,
                'tags': job.tags,
                'priority': job.priority,
                'next_run': next_run_str
            })
        # sort by priority desc
        out.sort(key=lambda x: x['priority'], reverse=True)
        return out

    def persist_jobs(self):
        """Persist jobs for all tenants."""
        if not self._persistence:
            return
        data = {}
        for job in self._jobs.values():
            # group by tenant
            tenant = job.tenant
            data.setdefault(tenant, {})
            data[tenant][job.job_id] = {
                'name': job.name,
                'tags': job.tags,
                'job_id': job.job_id,
                'next_run': job.run_time.isoformat(),
                'priority': job.priority
            }
        self._persistence.save(data)

    def load_jobs(self, tenant):
        """Load jobs for a tenant and return Job instances list."""
        if not self._persistence:
            return []
        data = self._persistence.load().get(tenant, {})
        jobs = []
        for jid, meta in data.items():
            run_time = datetime.fromisoformat(meta.get('next_run'))
            job = Job(tenant, jid, meta.get('name'), run_time, None, tags=meta.get('tags'))
            job.priority = meta.get('priority', 0)
            jobs.append(job)
        return jobs