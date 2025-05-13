"""
Command profiling for Translator CLI adapter.
"""
import time

def profile_command(*steps):
    results = {}
    for name, func in steps:
        start = time.time()
        func()
        results[name] = time.time() - start
    return results