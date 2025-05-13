import functools

def run_dry_run(func):
    """
    Decorator to capture operations in dry_run mode.
    The function to wrap must accept 'dry_run' param.
    Returns a tuple: (result, operations) if dry_run True, else normal result.
    """
    @functools.wraps(func)
    def wrapper(*args, dry_run=False, **kwargs):
        operations = []
        result = func(*args, dry_run=dry_run, operations=operations, **kwargs)
        if dry_run:
            return result, operations
        return result
    return wrapper
