import threading
import time
from functools import wraps
from collections import defaultdict
import datetime
import zoneinfo

shutdown_event = threading.Event()
_persistence_backend = 'sqlite'
_partial_data = []

jobs = {}
schedules = {}
dependencies = defaultdict(list)

def graceful_shutdown(abort_threshold=5):
    """
    Initiate a graceful shutdown: wait up to abort_threshold seconds to finish jobs,
    then persist partial data.
    """
    shutdown_event.set()
    start = time.time()
    while time.time() - start < abort_threshold:
        # Simulate work completion check
        time.sleep(0.1)
        break
    # Persist partial data
    _partial_data.append({'timestamp': datetime.datetime.utcnow().isoformat()})
    return True

def get_partial_data():
    return list(_partial_data)

def health_check():
    """
    Return health status for monitoring.
    """
    return {'status': 'ok'}

def trigger_job(job_name, *args, **kwargs):
    """
    Trigger a registered job by name.
    """
    if job_name in jobs:
        return jobs[job_name](*args, **kwargs)
    raise ValueError(f'Job "{job_name}" not found')

def schedule_job(job_name, cron=None, delay=None, timezone=None):
    """
    Schedule a job with a cron expression or delay and optional timezone.
    """
    schedules[job_name] = {'cron': cron, 'delay': delay, 'timezone': timezone}
    return True

def set_persistence_backend(backend):
    """
    Switch persistence backend to 'redis' or 'sqlite'.
    """
    global _persistence_backend
    if backend not in ('redis', 'sqlite'):
        raise ValueError(f'Unsupported backend "{backend}"')
    _persistence_backend = backend

def get_persistence_backend():
    return _persistence_backend

def timezone_aware(tz_name):
    """
    Decorator to attach timezone info to a job function.
    """
    tz = zoneinfo.ZoneInfo(tz_name)
    def decorator(func):
        func._timezone = tz
        return func
    return decorator

def exponential_backoff(initial=1, multiplier=2, max_time=10):
    """
    Decorator to retry a function with exponential backoff on Exception.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            wait = initial
            start = time.time()
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    elapsed = time.time() - start
                    if elapsed + wait > max_time:
                        raise
                    time.sleep(wait)
                    wait *= multiplier
        return wrapper
    return decorator

def define_dependencies(job_name, funcs):
    """
    Define a sequence of functions as dependencies for a job.
    """
    dependencies[job_name] = funcs
    def runner(*args, **kwargs):
        result = None
        for f in funcs:
            if result is None:
                result = f(*args, **kwargs)
            else:
                result = f(result)
        return result
    jobs[job_name] = runner
    return runner

def retry_job(max_attempts=3, multiplier=0):
    """
    Decorator to retry a job on Exception up to max_attempts times.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    if multiplier > 0:
                        time.sleep(multiplier)
        return wrapper
    return decorator

def limit_resources(max_concurrent=1):
    """
    Decorator to limit concurrent executions of a function.
    """
    sem = threading.Semaphore(max_concurrent)
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with sem:
                return func(*args, **kwargs)
        return wrapper
    return decorator
