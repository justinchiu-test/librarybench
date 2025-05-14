import signal

def handle_signals(cleanup_func):
    def handler(signum, frame):
        cleanup_func()
        # Normally would print aborted message
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return handler
