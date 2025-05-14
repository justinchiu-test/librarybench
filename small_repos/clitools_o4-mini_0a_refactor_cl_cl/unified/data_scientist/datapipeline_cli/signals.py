"""
Signal handling for data scientist CLI tools.
"""

import signal
from typing import Callable, List, Optional


# Global registry for signal handlers
_registered_handlers = []


def _get_registered() -> List[Callable]:
    """
    Get registered signal handlers.
    
    Returns:
        List[Callable]: List of registered handler functions.
    """
    return _registered_handlers


def handle_signals(cleanup_func: Callable) -> bool:
    """
    Register signal handlers for graceful shutdown.
    
    Args:
        cleanup_func (Callable): Function to call during cleanup.
        
    Returns:
        bool: True if registration was successful.
    """
    # Define signal handler
    def signal_handler(sig, frame):
        """Handle signal by running cleanup function."""
        if cleanup_func:
            cleanup_func()
    
    # Register handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Register handler for SIGTERM
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Add to registry
    _registered_handlers.append(cleanup_func)
    
    return True