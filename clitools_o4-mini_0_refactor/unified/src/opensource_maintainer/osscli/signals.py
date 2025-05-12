"""
Signal handler for open-source maintainers.
"""
import signal

def handle_signals(cmd):
    """
    Return a signal handler that performs cleanup for given command.
    """
    def handler(signum, frame):
        print(f"Cleanup after {cmd}")
    # Optionally register signals
    try:
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
    except Exception:
        pass
    return handler