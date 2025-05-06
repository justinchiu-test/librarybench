# Shared utility functions for running tasks with retries, backoff, timeouts, 
# and for recording metadata and sending alerts.

import time
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as _FutureTimeoutError

def compute_backoff(base_delay, factor, attempt):
    """Compute exponential backoff delay for a given attempt (1-based)."""
    return base_delay * (factor ** (attempt - 1))

def run_with_timeout(func, args=(), kwargs=None, timeout=None):
    """
    Run func(*args, **kwargs) enforcing a timeout in seconds.
    Returns (result, exception). If timeout expires, exception is TimeoutError.
    """
    if kwargs is None:
        kwargs = {}
    if timeout is None:
        try:
            return func(*args, **kwargs), None
        except Exception as e:
            return None, e

    # use thread to enforce timeout
    result_container = {}
    exc_container = {}
    def _target():
        try:
            result_container['value'] = func(*args, **kwargs)
        except Exception as e:
            exc_container['exc'] = e

    thread = threading.Thread(target=_target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        return None, TimeoutError(f"Function timed out after {timeout} seconds")
    if 'exc' in exc_container:
        return None, exc_container['exc']
    return result_container.get('value'), None

def retry_loop(func, args=(), kwargs=None, max_retries=0, 
               delay=0, backoff_factor=1, timeout=None, sleep_func=None):
    """
    Attempt to call func with retries, backoff, and timeout.
    Yields a tuple on each attempt: (attempt_number, result, exception).
    """
    if kwargs is None:
        kwargs = {}
    sleep = sleep_func or time.sleep
    for attempt in range(1, max_retries + 2):
        result, exc = run_with_timeout(func, args, kwargs, timeout)
        yield attempt, result, exc
        if exc is None:
            return
        if attempt <= max_retries:
            # compute delay and sleep before next retry
            d = compute_backoff(delay, backoff_factor, attempt)
            try:
                sleep(d)
            except Exception:
                pass

def record_metadata(metadata_storage, task_name, status, retries, start, end, exception=None):
    """
    Append a metadata record for a task run.
    """
    rec = {
        'status': status,
        'retries': retries,
        'start_time': start,
        'end_time': end,
        'execution_time': end - start,
        'exception': exception,
    }
    metadata_storage.append(task_name, rec)

def wrap_alert(alert_service, task_name, exception, metadata):
    """
    Send an alert for a failed task.
    """
    alert_service.send_alert(task_name, exception, metadata.copy())
