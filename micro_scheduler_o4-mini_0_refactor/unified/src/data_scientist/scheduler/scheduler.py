import time
import uuid

from scheduler.persistence.sqlite import SQLiteBackend
from scheduler.persistence.redis import RedisBackend

class Job:
    """Job representation for Data Scientist domain."""
    def __init__(self, job_id, func, timezone=None):
        self.id = job_id
        self.func = func
        self.dependencies = []
        self.timezone = timezone
        self.retry = (0, None)

class Scheduler:
    """Data Scientist domain-specific scheduler."""
    def __init__(self):
        self.jobs = {}
        self.persistence_backend = None
        self.resource_limits = {}
        self.shutting_down = False

    def set_persistence_backend(self, backend_type, options):
        if backend_type == 'sqlite':
            path = options.get('path')
            backend = SQLiteBackend(path)
        elif backend_type == 'redis':
            url = options.get('url', None)
            backend = RedisBackend(url)
        else:
            raise ValueError(f"Unknown backend {backend_type}")
        self.persistence_backend = backend
        return backend

    def schedule_job(self, func, job_id=None, timezone=None):
        if job_id is None:
            job_id = uuid.uuid4().hex
        job = Job(job_id, func, timezone=timezone)
        self.jobs[job_id] = job
        if self.persistence_backend:
            from scheduler.persistence.redis import RedisBackend as _RedisBackend
            if isinstance(self.persistence_backend, _RedisBackend):
                self.persistence_backend.save_job(job_id, {'id': job_id})
            else:
                self.persistence_backend.save_job(job_id, repr({'id': job_id}))
        return job_id

    def trigger_job(self, job_id):
        job = self.jobs.get(job_id)
        if not job:
            return None
        # run dependencies first
        for dep in job.dependencies:
            self.trigger_job(dep)
        max_retries, backoff_strategy = job.retry
        attempts = 0
        while True:
            attempts += 1
            try:
                result = job.func()
                return {'status': 'success', 'result': result, 'attempts': attempts}
            except Exception as e:
                if attempts > max_retries:
                    return {'status': 'failed', 'error': str(e), 'attempts': attempts}
                # calculate backoff delay
                if backoff_strategy == 'exponential':
                    delay = 2 ** (attempts - 1)
                else:
                    delay = 0
                time.sleep(delay)

    def define_dependencies(self, *args, **kwargs):
        if len(args) == 2:
            dep, job_id = args
        else:
            job_id = args[0]
            dep = kwargs.get('depends_on')
        deps = [dep] if not isinstance(dep, list) else dep
        self.jobs[job_id].dependencies = deps

    def retry_job(self, job_id, max_retries=None, backoff_strategy=None):
        job = self.jobs.get(job_id)
        if job:
            job.retry = (max_retries, backoff_strategy)

    def exponential_backoff(self, func):
        def wrapper(*args, **kwargs):
            attempts = 0
            max_retries = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempts >= max_retries:
                        raise
                    attempts += 1
                    time.sleep(2 ** (attempts - 1))
        return wrapper

    def limit_resources(self, **resources):
        self.resource_limits.update(resources)

    def health_check(self):
        return {'status': 'running', 'jobs': list(self.jobs.keys())}

    def graceful_shutdown(self, *args, **kwargs):
        self.shutting_down = True
        return True

__all__ = ['Scheduler', 'Job', 'SQLiteBackend', 'RedisBackend']