"""
MicroScheduler for Web Scraper domain, extending core scheduler for HTTP jobs.
"""
import time
import json
import pickle
import threading
import asyncio

import scheduler.scheduler as core_sched

class MicroScheduler(core_sched.Scheduler):
    """Scheduler for periodic web scraping tasks."""
    def __init__(self):
        super().__init__()
        # override core attributes
        self.jobs = {}            # job_id -> job info dict
        self.hooks = {}           # hook_name -> list of callables
        self.logger = None
        self._inflight_tasks = set()
        self.shutdown_flag = False

    def schedule_recurring_job(self, name, func, interval, tags=None):
        """Schedule a recurring job with interval in seconds."""
        next_run = time.time() + interval
        self.jobs[name] = {
            'name': name,
            'func': func,
            'interval': interval,
            'tags': tags or [],
            'last_status': None,
            'run_count': 0,
            'next_run': next_run,
        }
        return name

    def list_jobs(self):
        """List current job metadata."""
        out = []
        for job in self.jobs.values():
            out.append({
                'name': job['name'],
                'tags': job['tags'],
                'last_status': job['last_status'],
                'run_count': job['run_count'],
                'next_run': job['next_run'],
            })
        return out

    def adjust_interval(self, name, interval):
        """Adjust job interval and recompute next_run."""
        job = self.jobs.get(name)
        if not job:
            return
        job['interval'] = interval
        job['next_run'] = time.time() + interval

    def persist_jobs(self, filepath):
        """Persist jobs mapping to JSON or pickle based on file extension."""
        data = {}
        for name, job in self.jobs.items():
            data[name] = {
                'interval': job['interval'],
                'tags': job['tags'],
                'next_run': job['next_run'],
                'last_status': job['last_status'],
                'run_count': job['run_count'],
            }
        if filepath.endswith('.json'):
            with open(filepath, 'w') as f:
                json.dump(data, f)
        elif filepath.endswith('.pkl'):
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
        else:
            raise ValueError(f"Unsupported format {filepath}")

    def register_hook(self, name, func):
        """Register a single hook by name (override existing)."""
        self.hooks[name] = func

    def expose_metrics(self):
        """Expose simple metrics placeholders."""
        return {
            'histogram': {},
            'success_counter': {},
            'failure_counter': {},
            'queue_gauge': 0,
        }

    def attach_logger(self, logger):
        """Attach external logger."""
        self.logger = logger

    async def run_async_job(self, urls):
        """Perform asynchronous HTTP GETs for list of URLs."""
        results = []
        # launch aiohttp session via core scheduler module
        async with core_sched.aiohttp.ClientSession() as session:
            for url in urls:
                resp = await session.get(url)
                text = await resp.text()
                results.append({'url': url, 'status': resp.status, 'text': text})
        return results

    def graceful_shutdown(self, timeout=None):
        """Clear inflight tasks and set shutdown flag."""
        self.shutdown_flag = True
        self._inflight_tasks.clear()
        return True

    async def coordinate_leader_election(self, lock_name, timeout):
        """Attempt distributed lock via core scheduler.redis."""
        client = core_sched.redis.Redis()
        lock = client.lock(lock_name, timeout)
        acquired = lock.acquire(blocking=False)
        return acquired