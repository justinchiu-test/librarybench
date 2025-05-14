"""
Signal handling for CLI applications.

This module provides functionality for registering and handling OS signals.
"""

import signal
import sys
from typing import Dict, Callable, Any, List, Optional


class SignalHandler:
    """
    Signal handling manager for CLI applications.
    
    Manages registration and execution of signal handlers.
    """
    
    def __init__(self):
        """Initialize the signal handler."""
        self.handlers: Dict[int, List[Callable]] = {}
        self.original_handlers: Dict[int, Any] = {}
    
    def register(self, sig: int, handler: Callable, replace: bool = False) -> None:
        """
        Register a handler for a signal.
        
        Args:
            sig (int): Signal number (e.g., signal.SIGINT).
            handler (Callable): Function to call when signal is received.
            replace (bool): If True, replace existing handlers; if False, add to them.
        """
        # Store original signal handler if not already stored
        if sig not in self.original_handlers:
            self.original_handlers[sig] = signal.getsignal(sig)
        
        # Initialize or clear handlers list for this signal
        if sig not in self.handlers or replace:
            self.handlers[sig] = []
        
        # Add the new handler
        self.handlers[sig].append(handler)
        
        # Set our custom signal handler
        signal.signal(sig, self._handle_signal)
    
    def _handle_signal(self, sig: int, frame) -> None:
        """
        Handle a received signal by calling all registered handlers.
        
        Args:
            sig (int): Signal number.
            frame: Current stack frame.
        """
        if sig in self.handlers:
            for handler in self.handlers[sig]:
                try:
                    handler(sig, frame)
                except Exception as e:
                    print(f"Error in signal handler: {e}", file=sys.stderr)
    
    def unregister(self, sig: int, handler: Optional[Callable] = None) -> None:
        """
        Unregister a signal handler or all handlers for a signal.
        
        Args:
            sig (int): Signal number.
            handler (Callable, optional): Specific handler to remove. If None, remove all.
        """
        if sig not in self.handlers:
            return
        
        if handler is None:
            # Remove all handlers for this signal
            self.handlers[sig] = []
            # Restore original handler if available
            if sig in self.original_handlers:
                signal.signal(sig, self.original_handlers[sig])
                del self.original_handlers[sig]
        else:
            # Remove specific handler
            self.handlers[sig] = [h for h in self.handlers[sig] if h != handler]
    
    def reset_all(self) -> None:
        """Reset all signal handlers to their original state."""
        for sig, original_handler in self.original_handlers.items():
            signal.signal(sig, original_handler)
        
        self.handlers = {}
        self.original_handlers = {}


# Global signal handler instance
_signal_handler = SignalHandler()


def register_handler(sig: int, handler: Callable, replace: bool = False) -> None:
    """
    Register a signal handler.
    
    Args:
        sig (int): Signal number.
        handler (Callable): Handler function.
        replace (bool): Whether to replace existing handlers.
    """
    _signal_handler.register(sig, handler, replace)


def unregister_handler(sig: int, handler: Optional[Callable] = None) -> None:
    """
    Unregister a signal handler.
    
    Args:
        sig (int): Signal number.
        handler (Callable, optional): Handler to remove (None to remove all).
    """
    _signal_handler.unregister(sig, handler)


def reset_handlers() -> None:
    """Reset all signal handlers to their original state."""
    _signal_handler.reset_all()


def register_default_handlers() -> None:
    """
    Register default handlers for common signals.
    
    Provides graceful shutdown for SIGINT and SIGTERM.
    """
    def handle_shutdown(sig, frame):
        print("\nShutting down gracefully...")
        sys.exit(0)
    
    register_handler(signal.SIGINT, handle_shutdown)
    register_handler(signal.SIGTERM, handle_shutdown)