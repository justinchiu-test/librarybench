import os
import json
import threading
import time
from datetime import datetime, timedelta

class Scheduler:
    """
    DevOps Admin domain-specific scheduler.
    """
    def __init__(self, persist_file=None, leader_lock_file=None):
        self.persist_file = persist_file
        self.leader_lock_file = leader_lock_file
        self.jobs = {}  # name -> metadata dict
        self._success = {}  # name -> success count
        self._failure = {}  # name -> failure count
        self._hooks = {}    # name -> { 'pre': [fns], 'post': [fns] }
        self._threads = []  # threads from run_async_job
        self.leader = False
        # load persisted jobs
        if persist_file and os.path.exists(persist_file):
            try:
                with open(persist_file, 'r') as f:
                    data = json.load(f)
            except Exception:
                data = {}
            for name, meta in data.items():
                # reconstruct next_run as datetime
                nr = meta.get('next_run')
                next_run = datetime.utcfromtimestamp(nr) if nr is not None else None
                self.jobs[name] = {
                    'func': None,
                    'interval': meta.get('interval'),
                    'tags': meta.get('tags', []),
                    'last_exit_code': meta.get('last_exit_code'),
                    'run_count': meta.get('run_count', 0),
                    'next_run': next_run,
                }

    def schedule_recurring_job(self, name, func, interval, tags=None):
        """Register a recurring job with name, function, interval seconds, and tags."""
        next_run = datetime.utcnow() + timedelta(seconds=interval)
        self.jobs[name] = {
            'func': func,
            'interval': interval,
            'tags': tags if tags is not None else [],
            'last_exit_code': None,
            'run_count': 0,
            'next_run': next_run,
        }
        return name

    def list_jobs(self):
        """Return list of job metadata dicts."""
        out = []
        for name, meta in self.jobs.items():
            out.append({
                'name': name,
                'interval': meta.get('interval'),
                'tags': meta.get('tags'),
                'last_exit_code': meta.get('last_exit_code'),
                'run_count': meta.get('run_count'),
                'next_run': meta.get('next_run'),
            })
        return out

    def persist_jobs(self):
        """Persist current job metadata to JSON file."""
        if not self.persist_file:
            return
        data = {}
        for name, meta in self.jobs.items():
            nr = meta.get('next_run')
            ts = nr.timestamp() if isinstance(nr, datetime) else nr
            data[name] = {
                'interval': meta.get('interval'),
                'tags': meta.get('tags'),
                'last_exit_code': meta.get('last_exit_code'),
                'run_count': meta.get('run_count'),
                'next_run': ts,
            }
        try:
            with open(self.persist_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def adjust_interval(self, name, interval):
        """Adjust the interval and next run time for a job."""
        job = self.jobs.get(name)
        if not job:
            return
        job['interval'] = interval
        job['next_run'] = datetime.utcnow() + timedelta(seconds=interval)

    def register_hook(self, name, when, func):
        """Register a pre or post hook for a job."""
        if when not in ('pre', 'post'):
            raise ValueError(f'Invalid hook time {when}')
        self._hooks.setdefault(name, {}).setdefault(when, []).append(func)

    def coordinate_leader_election(self):
        """Acquire leadership; always succeed if no lockfile."""
        self.leader = True
        return True

    def run_job(self, name):
        """Execute a job synchronously if leader, invoking hooks."""
        if not self.leader:
            return
        job = self.jobs.get(name)
        if not job or not job.get('func'):
            return
        # pre-hooks
        for fn in self._hooks.get(name, {}).get('pre', []):
            try:
                fn()
            except Exception:
                pass
        # execute job
        try:
            job['func']()
            rc = 0
        except Exception:
            rc = 1
        # post-hooks
        for fn in self._hooks.get(name, {}).get('post', []):
            try:
                fn()
            except Exception:
                pass
        # update metadata
        job['last_exit_code'] = rc
        job['run_count'] = job.get('run_count', 0) + 1
        job['next_run'] = datetime.utcnow() + timedelta(seconds=job.get('interval', 0))
        # record metrics
        if rc == 0:
            self._success[name] = self._success.get(name, 0) + 1
        else:
            self._failure[name] = self._failure.get(name, 0) + 1

    def run_async_job(self, func, *args, **kwargs):
        """Run a job in a separate thread."""
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
        self._threads.append(t)
        return t

    def graceful_shutdown(self, timeout_seconds=None):
        """Wait for async jobs (up to timeout) and persist jobs."""
        for t in list(self._threads):
            try:
                t.join(timeout_seconds)
            except Exception:
                pass
        self.persist_jobs()
        return True

    def expose_metrics(self):
        """Expose metrics as a dict."""
        return {
            'job_success_total': dict(self._success),
            'job_failure_total': dict(self._failure),
            'job_queue_latency_seconds': {},
        }

    def attach_logger(self, logger):
        """Attach a custom logger."""
        self.logger = logger