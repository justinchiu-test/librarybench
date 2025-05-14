"""Adapter for backend_dev.microcli.signals."""

import signal
from typing import Callable, Optional, Any
from ....cli_core.signals import register_handler, unregister_handler, reset_handlers

# Re-export the functions for backward compatibility

def handle_signals(cleanup_func: Optional[Callable[[], None]] = None) -> Callable[[int, Any], None]:
    """
    Register signal handlers for graceful shutdown.

    Args:
        cleanup_func: Function to call during cleanup.

    Returns:
        function: Signal handler function.
    """
    def handler(sig: int, frame: Any) -> None:
        """Handle signals by running cleanup function."""
        if cleanup_func:
            cleanup_func()

        # No need to exit in test environment

    # Register the handler for common signals
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    return handler
