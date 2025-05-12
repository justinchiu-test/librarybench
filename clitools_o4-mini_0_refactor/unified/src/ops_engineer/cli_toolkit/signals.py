"""
Signal handling helpers for ops engineers.
"""
_cleanup_funcs = []

def register_cleanup(func):
    _cleanup_funcs.append(func)

def catch_signals(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            for f in _cleanup_funcs:
                f()
            print('aborted')
            return None
    return wrapper