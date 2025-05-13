"""
Signal handling for Operations Engineer CLI.
Provides cleanup registration and signal catching.
"""
_cleanup_funcs = []

def register_cleanup(func):
    _cleanup_funcs.append(func)

def catch_signals(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            for fn in _cleanup_funcs:
                fn()
            print("aborted")
            return None
    return wrapper