"""
Signal setup for security analysts.
"""
import signal

import sys

def handle_signals(cleanup_func, logger):
    """
    Register signal handlers that perform cleanup and log errors.
    """
    def handler(signum, frame):
        # invoke cleanup
        cleanup_func()
        # log error
        logger.error("aborted for security")
        # exit with error
        sys.exit(1)
    # register for SIGINT and SIGTERM
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return handler