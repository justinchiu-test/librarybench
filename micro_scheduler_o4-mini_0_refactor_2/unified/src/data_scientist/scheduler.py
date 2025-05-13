import threading
import time
import sqlite3
import uuid
from datetime import datetime
from functools import wraps
from zoneinfo import ZoneInfo

class SQLiteBackend:
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self._init_db()
    def _init_db(self):
        c = self.conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, data TEXT)')
        self.conn.commit()
    def save_job(self, job):
        c = self.conn.cursor()
        c.execute('REPLACE INTO jobs (id, data) VALUES (?,?)', (job.id, str(job.to_dict())))
        self.conn.commit()
    def load_job(self, job_id):
        c = self.conn.cursor()
        c.execute('SELECT data FROM jobs WHERE id=?', (job_id,))
        row = c.fetchone()
        return row[0] if row else None

class RedisBackend:
    def __init__(self, config=None):
        self.store = {}
    def save_job(self, job):
        self.store[job.id] = job.to_dict()
    def load_job(self, job_id):
        return self.store.get(job_id)

class Job:
    def __init__(self, id, func, cron=None, interval=None, start_offset=None, timezone='UTC'):
        self.id = id
        self.func = func
        self.cron = cron
        self.interval = interval
        self.start_offset = start_offset
        self.timezone = timezone
        self.dependencies = []
        self.max_retries = 0
        self.backoff_strategy = None
    def to_dict(self):
        return {
            'id': self.id,
            'cron': self.cron,
            'interval': self.interval,
            'start_offset': self.start_offset,
            'timezone': self.timezone,
            'dependencies': list(self.dependencies),
            'max_retries': self.max_retries
        }
    def run(self):
        attempts = 0
        delay = 1
        while True:
            try:
                result = self.func()
                return {'status': 'success', 'attempts': attempts + 1, 'result': result}
            except Exception as e:
                if attempts >= self.max_retries:
                    return {'status': 'failed', 'attempts': attempts + 1, 'error': str(e)}
                attempts += 1
                if self.backoff_strategy == 'exponential':
                    time.sleep(delay)
                    delay *= 2
                else:
                    time.sleep(0)

class Scheduler:
    def __init__(self):
        self.jobs = {}  # id -> Job
        self.persistence_backend = None
        self.resource_limits = {'cpu': None, 'gpu': None}
        self.shutting_down = False
    def set_persistence_backend(self, backend_type, config):
        if backend_type == 'sqlite':
            self.persistence_backend = SQLiteBackend(config['path'])
        elif backend_type == 'redis':
            self.persistence_backend = RedisBackend(config)
        else:
            raise ValueError("Unknown backend")
    def schedule_job(self, func, job_id=None, cron=None, interval=None, start_offset=None, timezone='UTC'):
        jid = job_id or str(uuid.uuid4())
        job = Job(jid, func, cron, interval, start_offset, timezone)
        self.jobs[jid] = job
        if self.persistence_backend:
            self.persistence_backend.save_job(job)
        return jid
    def trigger_job(self, job_id):
        if job_id not in self.jobs:
            return None
        job = self.jobs[job_id]
        # run dependencies first
        for dep in job.dependencies:
            self.trigger_job(dep)
        return job.run()
    def define_dependencies(self, parent_id, child_id):
        if parent_id in self.jobs and child_id in self.jobs:
            self.jobs[child_id].dependencies.append(parent_id)
        else:
            raise KeyError("Job id not found")
    def retry_job(self, job_id, max_retries, backoff_strategy=None):
        job = self.jobs[job_id]
        job.max_retries = max_retries
        job.backoff_strategy = backoff_strategy
    def exponential_backoff(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            max_retries = 3
            delay = 1
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempts >= max_retries:
                        raise
                    time.sleep(delay)
                    delay *= 2
                    attempts += 1
        return wrapper
    def limit_resources(self, cpu=None, gpu=None):
        self.resource_limits['cpu'] = cpu
        self.resource_limits['gpu'] = gpu
    def health_check(self):
        return {'status': 'running', 'jobs': list(self.jobs.keys())}
    def graceful_shutdown(self):
        self.shutting_down = True
    def timezone_aware(self, tz_name):
        tzinfo = ZoneInfo(tz_name)
        def decorator(func):
            func._timezone = tzinfo
            return func
        return decorator