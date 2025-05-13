import asyncio
import signal
import time
import json
import pickle
import logging

# Handle missing redis gracefully by providing a dummy module with a Redis class
try:
    import redis
except ImportError:
    class _DummyLock:
        def __init__(self, *args, **kwargs): pass
        def acquire(self, blocking=False): return False

    class _DummyRedisClient:
        def __init__(self, *args, **kwargs): pass
        def lock(self, name, timeout): return _DummyLock()

    class _DummyRedisModule:
        Redis = _DummyRedisClient

    redis = _DummyRedisModule()

import aiohttp

# Provide dummy metrics if prometheus_client is not available
try:
    from prometheus_client import Histogram, Counter, Gauge
except ImportError:
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass

    class Counter:
        def __init__(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass

    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass

class MicroScheduler:
    def __init__(self):
        self.jobs = {}
        self.hooks = {}
        self.logger = logging.getLogger(__name__)
        self.shutdown_flag = False
        self._inflight_tasks = set()
        # Metrics
        self._latency_histogram = Histogram('fetch_latency_seconds', 'HTTP fetch latency')
        self._success_counter = Counter('fetch_success_total', 'Successful fetches')
        self._failure_counter = Counter('fetch_failure_total', 'Failed fetches')
        self._queue_gauge = Gauge('queue_depth', 'Current queue depth')
        # Setup signal handler for graceful shutdown
        try:
            signal.signal(signal.SIGTERM, self._handle_signal)
        except Exception:
            pass

    def expose_metrics(self):
        return {
            'histogram': self._latency_histogram,
            'success_counter': self._success_counter,
            'failure_counter': self._failure_counter,
            'queue_gauge': self._queue_gauge,
        }

    def schedule_recurring_job(self, name, func, interval, tags=None):
        self.jobs[name] = {
            'func': func,
            'interval': interval,
            'tags': tags or [],
            'next_run': time.time() + interval,
            'last_status': None,
            'run_count': 0,
        }

    def attach_logger(self, logger):
        self.logger = logger

    def list_jobs(self):
        return [
            {
                'name': name,
                'next_run': info['next_run'],
                'last_status': info['last_status'],
                'run_count': info['run_count'],
                'tags': info['tags'],
            }
            for name, info in self.jobs.items()
        ]

    async def coordinate_leader_election(self, lock_name, ttl):
        client = redis.Redis()
        lock = client.lock(lock_name, timeout=ttl)
        acquired = lock.acquire(blocking=False)
        return acquired

    async def run_async_job(self, urls):
        session_obj = aiohttp.ClientSession()
        if asyncio.iscoroutine(session_obj):
            session = await session_obj
        else:
            session = session_obj

        self._queue_gauge.set(len(urls))

        tasks = []
        async with session:
            for url in urls:
                task = asyncio.create_task(self._fetch(session, url))
                self._inflight_tasks.add(task)
                task.add_done_callback(self._inflight_tasks.discard)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

        return results

    async def _fetch(self, session, url):
        start = time.time()
        try:
            resp_or_coro = session.get(url)
            if asyncio.iscoroutine(resp_or_coro):
                resp = await resp_or_coro
            else:
                resp = resp_or_coro

            text_coro = resp.text()
            if asyncio.iscoroutine(text_coro):
                await text_coro
            else:
                _ = text_coro

            latency = time.time() - start
            self._latency_histogram.observe(latency)
            if getattr(resp, 'status', None) == 200:
                self._success_counter.inc()
            else:
                self._failure_counter.inc()

            return {'url': url, 'status': resp.status}
        except Exception as e:
            self._failure_counter.inc()
            try:
                self.logger.error(json.dumps({'error': str(e), 'url': url}))
            except Exception:
                self.logger.error(f"Error fetching {url}: {e}")
            return {'url': url, 'error': str(e)}

    def register_hook(self, name, func):
        self.hooks[name] = func

    def adjust_interval(self, job_name, new_interval):
        if job_name in self.jobs:
            self.jobs[job_name]['interval'] = new_interval
            self.jobs[job_name]['next_run'] = time.time() + new_interval

    def persist_jobs(self, path):
        data = {
            name: {
                'interval': info['interval'],
                'tags': info['tags'],
                'next_run': info['next_run'],
                'last_status': info['last_status'],
                'run_count': info['run_count'],
            } for name, info in self.jobs.items()
        }
        ext = path.split('.')[-1].lower()
        if ext == 'json':
            with open(path, 'w') as f:
                json.dump(data, f)
        else:
            with open(path, 'wb') as f:
                pickle.dump(data, f)

    def graceful_shutdown(self, timeout):
        self.shutdown_flag = True
        self._inflight_tasks.clear()

    def _handle_signal(self, signum, frame):
        self.shutdown_flag = True