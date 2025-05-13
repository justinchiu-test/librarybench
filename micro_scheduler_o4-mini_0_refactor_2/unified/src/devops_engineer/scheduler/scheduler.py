from .persistence import PersistenceBackend, ShelveBackend, RedisBackend, SQLiteBackend

class Scheduler:
    def __init__(self):
        # job registry: id -> settings dict
        self.jobs = {}
        # persistence backend instance
        self.persistence = None
        # dependencies: job_id -> list of job_ids
        self.dependencies = {}
        # retry settings: job_id -> {'count', 'backoff'}
        self.retry_config = {}
        # resource limits: job_id -> dict
        self.resource_limits = {}
        # shutdown flag
        self.shutting_down = False

    def graceful_shutdown(self):
        self.shutting_down = True

    def health_check(self):
        return {'status': 'ok', 'jobs': list(self.jobs.keys())}

    def trigger_job(self, job_id):
        if job_id not in self.jobs:
            return None
        func = self.jobs[job_id].get('func')
        if not func:
            return None
        # dependencies first
        for dep in self.dependencies.get(job_id, []):
            self.trigger_job(dep)
        return func()

    def schedule_job(self, job_id, func=None, delay=None, interval=None, cron=None, timezone=None):
        # store job settings
        self.jobs[job_id] = {
            'func': func,
            'delay': delay,
            'interval': interval,
            'cron': cron,
            'timezone': timezone
        }

    def set_persistence_backend(self, backend):
        self.persistence = backend

    def exponential_backoff(self, base=1, factor=2):
        # exponential backoff: base * factor^(attempt-1)
        return lambda attempt: base * (factor ** (attempt - 1))

    def define_dependencies(self, job_id, depends_on=None):
        self.dependencies[job_id] = depends_on or []

    def retry_job(self, job_id, retry_count=None, backoff=None):
        self.jobs.setdefault(job_id, {})
        self.jobs[job_id]['retry'] = {'count': retry_count, 'backoff': backoff}

    def limit_resources(self, job_id, cpu=None, memory=None, io=None):
        self.resource_limits[job_id] = {'cpu': cpu, 'memory': memory, 'io': io}