import signal
import sys

def handle_signals(cleanup_func):
    """
    Set up signal handlers for graceful shutdown
    
    Args:
        cleanup_func: Function to call when signals are received
        
    Returns:
        callable: Signal handler function
    """
    def handler(sig, frame):
        cleanup_func()
        # Don't exit here, let the program decide what to do
    
    # Register the handler for common termination signals
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    
    return handler