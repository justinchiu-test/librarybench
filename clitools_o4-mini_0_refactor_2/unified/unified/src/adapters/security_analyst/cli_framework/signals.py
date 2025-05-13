"""
Signal handling for Security Analyst CLI.
"""
import sys
import signal

def handle_signals(cleanup, logger):
    """
    Register handlers for SIGINT and SIGTERM that call cleanup, log error, and exit.
    """
    def handler(signum, frame):
        cleanup()
        logger.error(f"aborted for security")
        sys.exit(1)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return handler