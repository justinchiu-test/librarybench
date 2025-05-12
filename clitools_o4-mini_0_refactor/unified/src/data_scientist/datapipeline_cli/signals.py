"""
Signal handling for data scientists.
"""
import signal

_registered = []

def handle_signals(func):
    def handler(signum, frame):
        func()
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    _registered.append(func)
    return True

def _get_registered():
    return list(_registered)