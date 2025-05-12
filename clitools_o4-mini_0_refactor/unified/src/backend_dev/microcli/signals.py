"""
Signal handling for backend developers.
"""
import signal

def handle_signals(func):
    def handler(signum, frame):
        func()
    # register handlers
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return handler