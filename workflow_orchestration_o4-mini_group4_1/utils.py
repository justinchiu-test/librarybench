# Shared utility functions for all modules
import threading
import time
from queue import Empty
from IT_Administrator.it_manager.alert import AlertManager
from IT_Administrator.it_manager.exceptions import TaskTimeoutError

def run_with_timeout(func, timeout, *args, **kwargs):
    """
    Run func in a thread and enforce a timeout.
    Raises TaskTimeoutError on timeout, or re-raises any exception from func.
    """
    result_container = {}
    exception_container = {}
    def target():
        try:
            result_container['value'] = func(*args, **kwargs)
        except Exception as e:
            exception_container['exception'] = e

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        raise TaskTimeoutError(f"Task timed out after {timeout} seconds")
    if 'exception' in exception_container:
        raise exception_container['exception']
    return result_container.get('value')

def safe_run(func, args, kwargs, failure_channel):
    """
    Call func(*args, **kwargs); on exception send an alert to failure_channel.
    """
    try:
        func(*args, **(kwargs or {}))
    except Exception as e:
        AlertManager.send_message(failure_channel, f"Job failed: {e}")

def collect_due_jobs(jobs, now):
    """
    Return the subset of jobs whose next_run() is <= now.
    """
    return [job for job in jobs if job.next_run() <= now]

def format_email(to, subject, body):
    return f"EMAIL to={to} subj={subject} body={body}"

def format_message(channel, message):
    return f"MSG channel={channel} msg={message}"
