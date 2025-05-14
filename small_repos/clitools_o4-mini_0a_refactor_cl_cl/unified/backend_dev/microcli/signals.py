"""Signal handling for backend developer CLI tools."""

import signal
from src.cli_core.signals import register_handler, unregister_handler, reset_handlers

def handle_signals(cleanup_func=None):
    """
    Register signal handlers for graceful shutdown.

    Args:
        cleanup_func: Function to call during cleanup.

    Returns:
        function: Signal handler function.
    """
    def handler(sig, frame):
        """Handle signals by running cleanup function."""
        if cleanup_func:
            cleanup_func()

        # No need to exit in test environment

    # Register the handler for common signals
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    return handler