import os
import threading
import time
import uuid
import json
import datetime
import inspect

from .job import Job
import types
try:
    import aiohttp
except ImportError:
    # provide dummy aiohttp for web_scraper domain
    aiohttp = types.SimpleNamespace(ClientSession=lambda *args, **kwargs: None)
# expose Redis for leader election
from .persistence.redis import RedisBackend
import types as _types
redis = _types.SimpleNamespace(Redis=RedisBackend)
from .persistence.file import FileBackend
from .events.hooks import HookManager
from .metrics.collector import MetricsCollector

class Scheduler:
    """
    Core unified scheduler supporting recurring and one-off jobs,
    persistence, hooks, and graceful shutdown.
    """
    def __init__(self, persist_path=None, leader_lock_file=None):
        self.jobs = {}
        self.persist_path = persist_path
        self.leader_lock_file = leader_lock_file
        self.leader = False
        self.hooks = HookManager()
        self.metrics = MetricsCollector()
        self._threads = []
        self._shutdown = threading.Event()
        self.shutting_down = False
        self.logger = None
        # load persisted state
        if persist_path and os.path.exists(persist_path):
            try:
                with open(persist_path) as f:
                    data = json.load(f)
                for jid, meta in data.items():
                    job = Job.from_dict(meta)
                    self.jobs[jid] = job
            except Exception:
                pass
    def schedule_recurring_job(self, func, interval, job_id=None):
        """Schedule a function to run periodically every `interval` seconds."""
        jid = job_id or uuid.uuid4().hex
        job = Job(jid, func, interval=interval)
        self.jobs[jid] = job
        # start thread
        t = threading.Thread(target=self._run_loop, args=(job,))
        t.daemon = True
        t.start()
        self._threads.append(t)
        return jid
    def _run_loop(self, job):
        # Run immediately, then continue at intervals
        first = True
        while not self._shutdown.is_set():
            if not first:
                # wait until next scheduled run, allowing interval adjustments
                while True:
                    if self._shutdown.is_set():
                        break
                    now = time.time()
                    next_run = job.next_run or 0
                    remaining = next_run - now
                    if remaining <= 0:
                        break
                    # sleep in small increments to respond to interval changes
                    time.sleep(min(remaining, 0.1))
                if self._shutdown.is_set():
                    break
            first = False
            # run job
            # logging start
            if self.logger:
                self.logger.info(f"Job {job.id} started")
            self.hooks.emit('start', job.id)
            start_time = time.time()
            try:
                _ = job.run()
                elapsed = time.time() - start_time
                self.metrics.record_latency(job.id, elapsed)
                self.metrics.increment_success(job.id)
                if self.logger:
                    self.logger.info(f"Job {job.id} succeeded")
                self.hooks.emit('success', job.id)
                job.count += 1
                job.last_status = 'success'
            except Exception as e:
                elapsed = time.time() - start_time
                self.metrics.record_latency(job.id, elapsed)
                self.metrics.increment_failure(job.id)
                if self.logger:
                    self.logger.error(f"Job {job.id} failed: {e}")
                self.hooks.emit('failure', job.id, e)
                job.last_status = 'failure'
            # schedule next run
            job.next_run = time.time() + job.interval
        # persist on thread exit
        if self.persist_path:
            self.persist_jobs()
    def schedule_job(self, func, **kwargs):
        # simple immediate run
        jid = kwargs.get('job_id') or uuid.uuid4().hex
        job = Job(jid, func, **kwargs)
        self.jobs[jid] = job
        return jid
    def trigger_job(self, job_id, *args, **kwargs):
        job = self.jobs.get(job_id)
        if not job:
            return None
        try:
            result = job.func(*args, **kwargs)
            return {'status': 'success', 'result': result, 'attempts': 1}
        except Exception as e:
            return {'status': 'failed', 'error': str(e), 'attempts': 1}
    def list_jobs(self):
        out = []
        for j in self.jobs.values():
            out.append(j.to_dict())
        return out
    def adjust_interval(self, job_id, interval):
        job = self.jobs.get(job_id)
        if job:
            job.interval = interval
            job.next_run = time.time() + interval
    def persist_jobs(self):
        """Persist current jobs metadata to JSON file."""
        if not self.persist_path:
            return
        try:
            data = {jid: job.to_dict() for jid, job in self.jobs.items()}
            with open(self.persist_path, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def graceful_shutdown(self, timeout=None):
        self.shutting_down = True
        self._shutdown.set()
        for t in self._threads:
            t.join(timeout)
        # remove leader lock
        if self.leader and self.leader_lock_file:
            try:
                os.remove(self.leader_lock_file)
            except OSError:
                pass
        return True
    def coordinate_leader_election(self):
        if not self.leader_lock_file:
            self.leader = True
            return True
        try:
            fd = os.open(self.leader_lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.close(fd)
            self.leader = True
            return True
        except FileExistsError:
            self.leader = False
            return False
    def expose_metrics(self):
        return self.metrics.render()
    def register_hook(self, event, func):
        valid = {'start', 'success', 'failure'}
        if event not in valid:
            raise ValueError(f"Invalid hook event {event}")
        self.hooks.register(event, func)
    def attach_logger(self, handler):
        import logging
        logger = logging.getLogger(f"Scheduler")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        self.logger = logger
    # advanced features
    def set_persistence_backend(self, *args, **kwargs):
        """Set custom persistence backend (not yet implemented)."""
        raise NotImplementedError
    def retry_job(self, *args, **kwargs):
        """Retry logic not implemented."""
        raise NotImplementedError
    def limit_resources(self, *args, **kwargs):
        """Resource limiting not implemented."""
        raise NotImplementedError
    def health_check(self):
        return {'status': 'running', 'jobs': list(self.jobs.keys())}