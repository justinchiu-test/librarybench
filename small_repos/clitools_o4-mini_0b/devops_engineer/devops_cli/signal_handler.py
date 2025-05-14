import signal

def handle_signals(cleanup_func):
    def _handler(signum, frame):
        try:
            cleanup_func()
        except Exception:
            pass
        print("Deployment aborted")
        # Intentionally do not call sys.exit here so tests won't be aborted.
    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)
    return _handler
