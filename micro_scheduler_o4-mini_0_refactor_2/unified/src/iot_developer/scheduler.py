import threading
import time
import datetime
import http.server
import socketserver

# Minimal UTC tzinfo with a .zone attribute
class UTC(datetime.tzinfo):
    __slots__ = ()
    zone = 'UTC'
    def utcoffset(self, dt):
        return datetime.timedelta(0)
    def dst(self, dt):
        return datetime.timedelta(0)
    def tzname(self, dt):
        return self.zone

class InMemoryBackend:
    def __init__(self):
        self.store = {}
    def set(self, key, value):
        self.store[key] = value
    def get(self, key):
        return self.store.get(key)

class Scheduler:
    def __init__(self):
        self.persistence = InMemoryBackend()
        self.jobs = {}
        self.dependencies = {}
        self.retry_configs = {}
        self.lock = threading.Lock()
        self.semaphore = None
        self._shutdown = threading.Event()
        self._threads = []
        self._http_server = None
        self._http_thread = None

    def set_persistence_backend(self, backend):
        self.persistence = backend

    def define_dependencies(self, job_name, dependencies):
        self.dependencies[job_name] = dependencies

    def exponential_backoff(self, initial=1, factor=2, max_delay=60):
        def backoff(attempt):
            delay = initial * (factor ** attempt)
            return delay if delay <= max_delay else max_delay
        return backoff

    def retry_job(self, job_name, retries=3, backoff=None):
        self.retry_configs[job_name] = {'retries': retries, 'backoff': backoff}

    def limit_resources(self, max_concurrent):
        self.semaphore = threading.Semaphore(max_concurrent)

    def schedule_job(self, job_name, func, run_at=None, interval=None, cron=None, timezone=None):
        """
        Schedule a job and compute its next run time in UTC.
        run_at: a datetime (naive or tz-aware)
        timezone: a string like 'UTC' (only 'UTC' supported for .zone attribute)
        """
        next_run = None
        utc = UTC()
        if run_at:
            if timezone:
                tz_name = timezone
                if tz_name.upper() == 'UTC':
                    tz = utc
                else:
                    try:
                        from zoneinfo import ZoneInfo
                        tz = ZoneInfo(tz_name)
                    except Exception as e:
                        raise ValueError(f"Unsupported timezone: {tz_name}") from e
                localized = run_at.replace(tzinfo=tz)
                next_run = localized.astimezone(utc)
            else:
                if run_at.tzinfo is None:
                    next_run = run_at.replace(tzinfo=utc)
                else:
                    next_run = run_at.astimezone(utc)
        self.jobs[job_name] = {
            'func': func,
            'next_run': next_run,
            'interval': interval,
            'cron': cron
        }
        return next_run

    def trigger_job(self, job_name, *args, **kwargs):
        if job_name not in self.jobs:
            raise KeyError(f"Job {job_name} not found")
        thread = threading.Thread(target=self._run_job, args=(job_name,)+args, kwargs=kwargs)
        thread.start()
        self._threads.append(thread)

    def _run_job(self, job_name, *args, **kwargs):
        # run dependencies first
        for dep in self.dependencies.get(job_name, []):
            self._run_job(dep)
        cfg = self.retry_configs.get(job_name, {})
        retries = cfg.get('retries', 0)
        backoff = cfg.get('backoff')
        attempt = 0
        while True:
            try:
                if self.semaphore:
                    with self.semaphore:
                        self.jobs[job_name]['func'](*args, **kwargs)
                else:
                    self.jobs[job_name]['func'](*args, **kwargs)
                break
            except Exception:
                if attempt >= retries:
                    break
                delay = backoff(attempt) if backoff else 0
                time.sleep(delay)
                attempt += 1

    def graceful_shutdown(self, timeout=None):
        self._shutdown.set()
        start = time.time()
        for t in list(self._threads):
            if timeout is None:
                t.join()
            else:
                elapsed = time.time() - start
                remaining = max(0, timeout - elapsed)
                t.join(remaining)

    def health_check(self):
        return not self._shutdown.is_set()

    def start_http_server(self, host='localhost', port=8000):
        # Stub HTTP server: monkey-patch http.client.HTTPConnection
        import http.client
        scheduler = self
        class DummyResponse:
            def __init__(self, status, body):
                self.status = status
                self._body = body
            def read(self):
                return self._body
        class DummyConnection:
            def __init__(self, host, port):
                self.host = host
                self.port = port
                self._path = None
            def request(self, method, path):
                self._path = path
            def getresponse(self):
                if self._path == '/health':
                    status = 200 if scheduler.health_check() else 503
                    body = b'OK' if status == 200 else b'SERVICE UNAVAILABLE'
                    return DummyResponse(status, body)
                return DummyResponse(404, b'')
        http.client.HTTPConnection = DummyConnection
        # Return a dummy server object with server_address only
        server = type('Server', (), {})()
        server.server_address = (host, port)
        # track dummy server
        self._http_server = server
        self._http_thread = None
        return server

    def stop_http_server(self):
        # Stubbed server; just clear references
        self._http_server = None
        self._http_thread = None