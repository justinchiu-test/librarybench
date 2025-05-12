"""
Signal handler decorator for devops engineers.
"""
import signal

def handle_signals(func):
    def handler(signum, frame):
        func()
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return handler