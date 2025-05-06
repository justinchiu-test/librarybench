import threading

def run_with_timeout(func, args=None, kwargs=None, timeout=None):
    """
    Run a callable with a timeout. Raises TimeoutError if the call
    does not complete within `timeout` seconds.
    """
    args = args or ()
    kwargs = kwargs or {}
    if timeout is None:
        return func(*args, **kwargs)
    result = {}
    def target():
        try:
            result['value'] = func(*args, **kwargs)
        except Exception as e:
            result['exception'] = e
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        raise TimeoutError(f"Function '{func.__name__}' timed out after {timeout} seconds")
    if 'exception' in result:
        raise result['exception']
    return result.get('value')

def get_due_jobs(jobs, now):
    """
    Given a list of ScheduledJob instances and a datetime `now`,
    return those whose next_run() is <= now.
    """
    return [job for job in jobs if job.next_run() <= now]

def format_message(prefix: str, **fields):
    """
    Format an alert or log message with a prefix and key=value pairs.
    """
    parts = [f"{k}={v}" for k, v in fields.items()]
    return f"{prefix} " + " ".join(parts)
