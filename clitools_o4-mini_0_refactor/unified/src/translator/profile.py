"""
Profile execution time for translator commands.
"""
import time

def profile_command(*steps):
    """
    steps: sequence of (name, func) tuples.
    Returns dict mapping name to elapsed time in seconds.
    """
    results = {}
    for name, func in steps:
        start = time.time()
        func()
        elapsed = time.time() - start
        results[name] = elapsed
    return results