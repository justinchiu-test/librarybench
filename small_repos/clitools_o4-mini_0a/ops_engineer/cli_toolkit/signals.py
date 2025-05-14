import signal
import sys

_cleanup_funcs = []

def register_cleanup(func):
    _cleanup_funcs.append(func)

def catch_signals(func):
    """
    Decorator to catch KeyboardInterrupt/SystemExit, run cleanup, and print message.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            for f in _cleanup_funcs:
                try:
                    f()
                except Exception:
                    pass
            print("aborted")
            return None
    return wrapper
