"""
Signal handling for the CLI Toolkit.
"""
import signal
import sys
import functools
from typing import Callable, List, Optional


_cleanup_handlers: List[Callable] = []


def register_cleanup(handler: Callable) -> None:
    """
    Register a cleanup handler to be called when signals are received.
    
    Args:
        handler: Function to call during cleanup
    """
    _cleanup_handlers.append(handler)


def _run_cleanup_handlers() -> None:
    """Run all registered cleanup handlers."""
    for handler in _cleanup_handlers:
        try:
            handler()
        except Exception as e:
            print(f"Error in cleanup handler: {e}", file=sys.stderr)


def catch_signals(func: Callable) -> Callable:
    """
    Decorator to catch signals and run cleanup handlers.
    
    Args:
        func: Function to wrap
    
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\nOperation aborted by user.", file=sys.stderr)
            _run_cleanup_handlers()
            return None
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            _run_cleanup_handlers()
            raise
    
    return wrapper


def setup_signal_handlers() -> None:
    """Set up signal handlers for the application."""
    # Handle SIGINT (Ctrl+C)
    def sigint_handler(sig, frame):
        print("\nOperation aborted by user.", file=sys.stderr)
        _run_cleanup_handlers()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, sigint_handler)
    
    # Handle SIGTERM
    def sigterm_handler(sig, frame):
        print("\nReceived termination signal.", file=sys.stderr)
        _run_cleanup_handlers()
        sys.exit(1)
    
    signal.signal(signal.SIGTERM, sigterm_handler)