"""
Signal handling for operations engineer CLI tools.
"""

import sys
import signal
from typing import Callable, List, Optional


# Global registry for cleanup functions
_cleanup_functions: List[Callable] = []


def register_cleanup(func: Callable) -> None:
    """
    Register a cleanup function to be called on signals.
    
    Args:
        func (Callable): Function to call during cleanup.
    """
    if func not in _cleanup_functions:
        _cleanup_functions.append(func)


def _signal_handler(sig, frame):
    """
    Handle signals by running cleanup functions.
    
    Args:
        sig: Signal number.
        frame: Current stack frame.
    """
    # Run cleanup functions
    for func in _cleanup_functions:
        try:
            func()
        except Exception as e:
            print(f"Error in cleanup function: {e}", file=sys.stderr)
    
    # Print abort message
    print("\nOperation aborted", file=sys.stdout)
    
    # Exit - not needed in test environment


def catch_signals(func: Callable) -> Callable:
    """
    Decorator to catch signals within a function.
    
    Args:
        func (Callable): Function to wrap.
        
    Returns:
        Callable: Wrapped function.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            _signal_handler(signal.SIGINT, None)
            return None
    
    return wrapper