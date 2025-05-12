import threading
import time
from datetime import datetime

from .persistence import PersistenceBackend

class Job:
    """Representation of a job with parameters and state."""
    def __init__(self, job_id, func=None, delay=None, interval=None, cron=None, timezone=None):
        self.job_id = job_id
        self.func = func
        self.delay = delay
        self.interval = interval
        self.cron = cron
        self.timezone = timezone
        self.dependencies = []
        self.retry = None

class Scheduler:
    """DevOps Engineer domain-specific scheduler."""
    def __init__(self):
        self.jobs = {}  # job_id -> Job
        self.dependencies = {}  # job_id -> list of job_ids it depends on
        self.resource_limits = {}  # job_id or global -> limits dict
        self.persistence = None
        self.shutting_down = False

    def schedule_job(self, job_id, func=None, delay=None, interval=None, cron=None, timezone=None):
        """Register a job with parameters."""
        job = {
            'func': func,
            'delay': delay,
            'interval': interval,
            'cron': cron,
            'timezone': timezone,
            'dependencies': [],
            'retry': None,
        }
        self.jobs[job_id] = job
        return job_id

    def trigger_job(self, job_id):
        """Trigger a job, running its dependencies first."""
        job = self.jobs.get(job_id)
        if not job:
            return None
        # run dependencies
        for dep in job.get('dependencies', []):
            self.trigger_job(dep)
        # execute job function
        func = job.get('func')
        if func is None:
            return None
        return func()

    def health_check(self):
        """Return health status and list of jobs."""
        return {'status': 'ok', 'jobs': list(self.jobs.keys())}

    def set_persistence_backend(self, backend):
        """Set persistence backend instance."""
        self.persistence = backend

    def define_dependencies(self, job_id, depends_on=None):
        """Set dependencies for a job."""
        if depends_on is None:
            return
        # record in mapping
        self.dependencies[job_id] = depends_on
        # also update job config if exists
        job = self.jobs.get(job_id)
        if job is not None:
            job['dependencies'] = depends_on

    def retry_job(self, job_id, retry_count=None, backoff=None):
        """Configure retry settings for a job."""
        if job_id not in self.jobs:
            return
        self.jobs[job_id]['retry'] = {'count': retry_count, 'backoff': backoff}

    def limit_resources(self, job_id=None, **resources):
        """Set resource limits for a job or global."""
        if job_id:
            self.resource_limits[job_id] = resources
        else:
            for key, val in resources.items():
                self.resource_limits[key] = val

    def exponential_backoff(self, base=1, factor=2):
        """Return exponential backoff function."""
        def fn(attempt):
            # attempt starts at 1
            return base * (factor ** (attempt - 1))
        return fn

    def graceful_shutdown(self):
        """Graceful shutdown setting flag."""
        self.shutting_down = True