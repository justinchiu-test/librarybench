"""
Signal handling for Data Pipeline CLI.
"""
import signal
import sys
import logging
from typing import Callable, Dict, Optional

# Set up logger
logger = logging.getLogger(__name__)

class SignalHandler:
    """
    Handles signals for graceful shutdown.
    """
    
    def __init__(self):
        """Initialize a new signal handler."""
        self.handlers: Dict[int, Callable] = {}
        self.original_handlers: Dict[int, Callable] = {}
        self.exit_code = 0
    
    def register(self, sig: int, handler: Callable) -> None:
        """
        Register a handler for a signal.
        
        Args:
            sig: Signal number
            handler: Handler function
        """
        # Store original handler
        self.original_handlers[sig] = signal.getsignal(sig)
        
        # Register our handler
        self.handlers[sig] = handler
        signal.signal(sig, self._handle_signal)
        
        logger.debug(f"Registered handler for signal {sig}")
    
    def unregister(self, sig: int) -> None:
        """
        Unregister a handler for a signal.
        
        Args:
            sig: Signal number
        """
        if sig in self.original_handlers:
            # Restore original handler
            signal.signal(sig, self.original_handlers[sig])
            
            # Clean up
            del self.original_handlers[sig]
            if sig in self.handlers:
                del self.handlers[sig]
            
            logger.debug(f"Unregistered handler for signal {sig}")
    
    def unregister_all(self) -> None:
        """Unregister all signal handlers."""
        for sig in list(self.original_handlers.keys()):
            self.unregister(sig)
    
    def _handle_signal(self, sig: int, frame) -> None:
        """
        Handle a signal.
        
        Args:
            sig: Signal number
            frame: Current stack frame
        """
        logger.debug(f"Received signal {sig}")
        
        # Call our handler
        if sig in self.handlers:
            try:
                self.handlers[sig](sig, frame)
            except Exception as e:
                logger.error(f"Error in signal handler: {e}")
                self.exit_code = 1
                sys.exit(1)

# Global signal handler
_signal_handler = SignalHandler()

def handle_sigint(sig: int, frame) -> None:
    """
    Default SIGINT handler.
    
    Args:
        sig: Signal number
        frame: Current stack frame
    """
    logger.info("Received SIGINT, shutting down...")
    sys.exit(0)

def handle_sigterm(sig: int, frame) -> None:
    """
    Default SIGTERM handler.
    
    Args:
        sig: Signal number
        frame: Current stack frame
    """
    logger.info("Received SIGTERM, shutting down...")
    sys.exit(0)

def register_default_handlers() -> None:
    """Register default signal handlers."""
    _signal_handler.register(signal.SIGINT, handle_sigint)
    _signal_handler.register(signal.SIGTERM, handle_sigterm)

def unregister_default_handlers() -> None:
    """Unregister default signal handlers."""
    _signal_handler.unregister(signal.SIGINT)
    _signal_handler.unregister(signal.SIGTERM)

def register(sig: int, handler: Callable) -> None:
    """
    Register a signal handler.
    
    Args:
        sig: Signal number
        handler: Handler function
    """
    _signal_handler.register(sig, handler)

def unregister(sig: int) -> None:
    """
    Unregister a signal handler.
    
    Args:
        sig: Signal number
    """
    _signal_handler.unregister(sig)

def unregister_all() -> None:
    """Unregister all signal handlers."""
    _signal_handler.unregister_all()


# Registry for cleanup handlers
_cleanup_handlers = []

def handle_signals(cleanup_handler: Callable) -> bool:
    """
    Register signal handlers that will call the cleanup function.
    
    Args:
        cleanup_handler: Function to call when signals are received
        
    Returns:
        True if handlers were registered successfully
    """
    try:
        # Register the cleanup handler
        _cleanup_handlers.append(cleanup_handler)
        
        # Create a signal handler that calls the cleanup function
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, cleaning up...")
            try:
                cleanup_handler()
            except Exception as e:
                logger.error(f"Error in cleanup handler: {e}")
            finally:
                # Exit with the appropriate code
                sys.exit(0)
        
        # Register for SIGINT and SIGTERM
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        return True
    except Exception as e:
        logger.error(f"Error registering signal handlers: {e}")
        return False


def _get_registered() -> list:
    """
    Get the list of registered cleanup handlers.
    
    Returns:
        List of cleanup handlers
    """
    return _cleanup_handlers