import time

def profile_command(*steps):
    """
    Execute named steps and measure their execution time.
    Steps should be provided as tuples: (name, callable).
    Returns a dict mapping step names to elapsed time in seconds.
    """
    results = {}
    for name, step in steps:
        start = time.time()
        step()
        end = time.time()
        results[name] = end - start
    return results
