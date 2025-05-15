import signal

_registered_callbacks = []

def handle_signals(callback):
    def handler(signum, frame):
        callback()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handler)
    _registered_callbacks.append(callback)
    return True

def _get_registered():
    return list(_registered_callbacks)
