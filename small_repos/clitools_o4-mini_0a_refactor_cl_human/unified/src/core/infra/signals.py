"""
Signal handling module for CLI tools.
Manages signal handling and cleanup for graceful interruption.
"""

import atexit
import signal
from typing import Any, Callable, Dict, List, Optional, Set, Union


class SignalHandler:
    """Manages signal handling for graceful interruption."""
    
    def __init__(self, app_name: str = "application"):
        """
        Initialize a new signal handler.
        
        Args:
            app_name: Name of the application (for logging)
        """
        self.app_name = app_name
        self.handlers: Dict[int, List[Callable[..., Any]]] = {}
        self.exit_handlers: List[Callable[..., Any]] = []
        self.original_handlers: Dict[int, Any] = {}
        self.initialized = False
    
    def register_signal_handler(self, 
                              signals: Union[int, List[int]], 
                              handler: Callable[..., Any],
                              prepend: bool = False) -> None:
        """
        Register a handler for one or more signals.
        
        Args:
            signals: Signal number(s) to handle
            handler: Function to call when the signal is received
            prepend: Whether to prepend to the handler list (default: append)
        """
        if isinstance(signals, int):
            signals = [signals]
        
        for sig in signals:
            if sig not in self.handlers:
                self.handlers[sig] = []
            
            if prepend:
                self.handlers[sig].insert(0, handler)
            else:
                self.handlers[sig].append(handler)
    
    def register_exit_handler(self, 
                            handler: Callable[..., Any],
                            prepend: bool = False) -> None:
        """
        Register a handler to run at application exit.
        
        Args:
            handler: Function to call at exit
            prepend: Whether to prepend to the handler list (default: append)
        """
        if prepend:
            self.exit_handlers.insert(0, handler)
        else:
            self.exit_handlers.append(handler)
        
        # Also register with atexit
        atexit.register(handler)
    
    def initialize(self) -> None:
        """
        Initialize signal handling.
        Registers handlers for common signals.
        """
        if self.initialized:
            return
        
        # Store original handlers
        signals_to_handle = [
            signal.SIGINT,   # Ctrl+C
            signal.SIGTERM,  # Termination
        ]
        
        # Handle SIGHUP if available (not on Windows)
        try:
            signals_to_handle.append(signal.SIGHUP)
        except AttributeError:
            pass
        
        for sig in signals_to_handle:
            self.original_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, self._handle_signal)
        
        self.initialized = True
    
    def _handle_signal(self, signum: int, frame) -> None:
        """
        Handle a received signal.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        # Show a message
        if signum == signal.SIGINT:
            print(f"\nInterrupting {self.app_name}...")
        elif signum == signal.SIGTERM:
            print(f"\nTerminating {self.app_name}...")
        else:
            print(f"\nReceived signal {signum}, shutting down {self.app_name}...")
        
        # Call registered handlers
        if signum in self.handlers:
            for handler in self.handlers[signum]:
                try:
                    handler()
                except Exception as e:
                    print(f"Error in signal handler: {e}")
        
        # Call exit handlers
        for handler in self.exit_handlers:
            try:
                handler()
            except Exception as e:
                print(f"Error in exit handler: {e}")
        
        # Restore original handler and resend signal
        if signum in self.original_handlers:
            original = self.original_handlers[signum]
            signal.signal(signum, original)
            if signum == signal.SIGINT:
                # For SIGINT, raise KeyboardInterrupt for cleaner exit
                raise KeyboardInterrupt()
            else:
                # For other signals, re-raise the signal
                signal.raise_signal(signum)
    
    def shutdown(self) -> None:
        """
        Shutdown the signal handler.
        Restores original signal handlers.
        """
        if not self.initialized:
            return
        
        # Restore original handlers
        for sig, handler in self.original_handlers.items():
            signal.signal(sig, handler)
        
        self.initialized = False


# Create a global handler for convenience
_global_handler = SignalHandler()

def register_signal_handler(signals: Union[int, List[int]], 
                          handler: Callable[..., Any],
                          prepend: bool = False) -> None:
    """Register a handler for signals with the global handler."""
    _global_handler.register_signal_handler(signals, handler, prepend)

def register_exit_handler(handler: Callable[..., Any],
                        prepend: bool = False) -> None:
    """Register an exit handler with the global handler."""
    _global_handler.register_exit_handler(handler, prepend)

def initialize() -> None:
    """Initialize the global signal handler."""
    _global_handler.initialize()

def shutdown() -> None:
    """Shutdown the global signal handler."""
    _global_handler.shutdown()