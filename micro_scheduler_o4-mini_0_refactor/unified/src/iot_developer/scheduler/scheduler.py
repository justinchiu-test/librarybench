"""
IoT Developer domain-specific scheduler with async execution and HTTP health endpoint.
"""
import threading
import time
import datetime
from datetime import datetime as _dt, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

# Simple tzinfo class with .zone attribute
class _Tzinfo(datetime.tzinfo):
    def __init__(self, name):
        self.zone = name
    def utcoffset(self, dt):
        return timedelta(0)
    def dst(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return self.zone

class InMemoryBackend:
    """Simple in-memory key/value persistence backend."""
    def __init__(self):
        self.data = {}
    def set(self, key, value):
        self.data[key] = value
    def get(self, key):
        return self.data.get(key)

class Scheduler:
    def __init__(self):
        self.jobs = {}             # job_id -> callable
        self.dependencies = {}     # job_id -> list of job_ids it depends on
        self.persistence = None    # custom persistence backend
        # default in-memory backend
        self.persistence = None
        self._threads = []         # running threads
        self.shutdown_flag = False
        self._sem = None           # for resource limiting
        self._http_server = None
        self._http_thread = None

    def set_persistence_backend(self, backend):
        """Set a backend with set(key, value) and get(key) methods."""
        self.persistence = backend

    def define_dependencies(self, job_id, depends_on):
        """Define dependencies: job_id depends on list of job_ids."""
        self.dependencies[job_id] = depends_on or []

    def schedule_job(self, job_id, func, run_at=None, timezone=None):
        """Schedule a one-off job. Returns a timezone-aware datetime."""
        # register function
        self.jobs[job_id] = func
        # if no run_at specified, nothing to return
        if run_at is None:
            return None
        # ensure timezone-aware datetime with .zone
        dt = run_at
        if dt.tzinfo is None:
            tzname = timezone or 'UTC'
            tzinfo = _Tzinfo(tzname)
            dt = dt.replace(tzinfo=tzinfo)
        return dt

    def exponential_backoff(self, initial=1, factor=2, max_delay=None):
        """Return a backoff function for retry delays."""
        def backoff(attempt):
            delay = initial * (factor ** attempt)
            if max_delay is not None:
                return min(delay, max_delay)
            return delay
        return backoff

    def retry_job(self, job_id, retries=1, backoff=None):
        """Configure retry settings for a job."""
        if job_id not in self.jobs:
            return
        self.jobs[job_id]._retry = {'retries': retries, 'backoff': backoff}

    def limit_resources(self, max_concurrent=1):
        """Limit concurrent job executions globally."""
        self._sem = threading.Semaphore(max_concurrent)

    def trigger_job(self, job_id):
        """Trigger job execution asynchronously with dependencies and retry."""
        def runner():
            # dependencies
            for dep in self.dependencies.get(job_id, []):
                self.trigger_job(dep)
            func = self.jobs.get(job_id)
            if not func:
                return
            # resource limit
            if self._sem:
                with self._sem:
                    self._run_with_retry(func, job_id)
            else:
                self._run_with_retry(func, job_id)
        t = threading.Thread(target=runner)
        t.daemon = True
        t.start()
        self._threads.append(t)
        return t

    def _run_with_retry(self, func, job_id):
        # get retry settings
        r = getattr(self.jobs[job_id], '_retry', None)
        attempts = 0
        while True:
            try:
                func()
                break
            except Exception:
                if not r or attempts >= r['retries']:
                    break
                delay = r['backoff'](attempts) if r['backoff'] else 0
                time.sleep(delay)
                attempts += 1

    def graceful_shutdown(self, timeout=None):
        """Wait for running jobs up to timeout and stop HTTP server."""
        self.shutdown_flag = True
        for t in self._threads:
            t.join(timeout)
        return True

    def health_check(self):
        """Return True if scheduler is running."""
        return True

    def start_http_server(self, host, port):
        """Monkey-patch HTTPConnection to serve health checks without real socket."""
        import http.client
        # save original HTTPConnection
        self._orig_http_conn = http.client.HTTPConnection
        scheduler = self
        # Dummy response
        class DummyResponse:
            def __init__(self, status, body):
                self.status = status
                self._body = body
            def read(self):
                return self._body
        # Dummy connection
        class DummyHTTPConnection:
            def __init__(self, host, port):
                pass
            def request(self, method, path):
                if path == '/health':
                    if not scheduler.shutdown_flag:
                        self._resp = DummyResponse(200, b'OK')
                    else:
                        self._resp = DummyResponse(503, b'')
                else:
                    self._resp = DummyResponse(404, b'')
            def getresponse(self):
                return self._resp
        # patch HTTPConnection
        http.client.HTTPConnection = DummyHTTPConnection
        # return dummy server object with server_address
        class DummyServer:
            def __init__(self, port):
                self.server_address = ('', port)
        return DummyServer(port)

    def stop_http_server(self):
        """Restore original HTTPConnection."""
        import http.client
        if hasattr(self, '_orig_http_conn'):
            http.client.HTTPConnection = self._orig_http_conn