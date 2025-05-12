"""
Finance Analyst domain-specific scheduler module.
"""
import threading
import time
from datetime import datetime
import zoneinfo

# Global state
shutdown_event = threading.Event()
_partial_data = []
jobs = {}        # job_name -> callable or runner
dependencies = {} # job_name -> dependency configuration
schedules = {}   # job_name -> schedule config dict
_persistence_backend = None

def set_persistence_backend(backend_name):
    """Set the persistence backend type ('sqlite' or 'redis')."""
    global _persistence_backend
    if backend_name not in ('sqlite', 'redis'):
        raise ValueError(f"Unknown backend {backend_name}")
    _persistence_backend = backend_name

def get_persistence_backend():
    return _persistence_backend

def graceful_shutdown(abort_threshold=None):
    """Perform graceful shutdown and record partial data."""
    shutdown_event.set()
    # record partial data entry
    entry = {'timestamp': datetime.now()}
    _partial_data.append(entry)
    return True

def get_partial_data():
    """Return partial data collected during runtime."""
    return list(_partial_data)

def health_check():
    """Return health status."""
    return {'status': 'ok'}

def trigger_job(job_name, *args, **kwargs):
    """Trigger a registered job by name."""
    if job_name not in jobs:
        raise ValueError(f"Job {job_name} not found")
    fn = jobs[job_name]
    return fn(*args, **kwargs)

def schedule_job(job_name, cron=None, delay=None, timezone=None):
    """Record a job schedule configuration."""
    cfg = {}
    if cron is not None:
        cfg['cron'] = cron
    if delay is not None:
        cfg['delay'] = delay
    if timezone is not None:
        cfg['timezone'] = timezone
    schedules[job_name] = cfg
    return True

def timezone_aware(tz_name):
    """Decorator to attach timezone info to a function."""
    def decorator(fn):
        tz = zoneinfo.ZoneInfo(tz_name)
        setattr(fn, '_timezone', tz)
        return fn
    return decorator

def exponential_backoff(initial=1, multiplier=2, max_time=0):
    """Decorator for retrying fn with exponential backoff until max time."""
    def decorator(fn):
        def wrapper(*args, **kwargs):
            start = time.time()
            delay = initial
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    now = time.time()
                    if max_time and now - start + delay > max_time:
                        raise
                    time.sleep(delay)
                    delay *= multiplier
        return wrapper
    return decorator

def define_dependencies(name, funcs):
    """Define a sequence of functions to run as a dependency chain."""
    def runner():
        result = None
        for f in funcs:
            if result is None:
                result = f()
            else:
                result = f(result)
        return result
    jobs[name] = runner
    return runner

def retry_job(max_attempts, multiplier=1):
    """Decorator to retry a function on failure up to max attempts."""
    def decorator(fn):
        def wrapper(*args, **kwargs):
            attempts = 0
            last_exc = None
            while attempts < max_attempts:
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    attempts += 1
            # after max attempts, raise last exception
            raise last_exc
        return wrapper
    return decorator

def limit_resources(max_concurrent=1):
    """Decorator to limit concurrent executions."""
    sem = threading.Semaphore(max_concurrent)
    def decorator(fn):
        def wrapper(*args, **kwargs):
            with sem:
                return fn(*args, **kwargs)
        return wrapper
    return decorator