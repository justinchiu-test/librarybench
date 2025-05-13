"""
Signal handling for backend_dev microcli.
Registers a cleanup handler for SIGINT and SIGTERM.
"""
import signal

def handle_signals(cleanup):
    """
    Register cleanup() to be called on SIGINT and SIGTERM.
    Returns the handler function.
    """
    def handler(signum, frame):
        cleanup()
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return handler