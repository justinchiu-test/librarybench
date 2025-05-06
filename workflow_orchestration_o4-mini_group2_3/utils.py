import time

def safe_run(func, args=(), kwargs=None):
    """
    Execute func(*args, **kwargs), returning (True, result, None) on success,
    or (False, None, exception) on failure.
    """
    if kwargs is None:
        kwargs = {}
    try:
        return True, func(*args, **kwargs), None
    except Exception as exc:
        return False, None, exc
