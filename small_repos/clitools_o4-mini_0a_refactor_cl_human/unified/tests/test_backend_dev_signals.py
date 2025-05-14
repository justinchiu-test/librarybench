import signal
from src.core.infra.signals import SignalHandler

def test_handlers_registered():
    # Create a signal handler
    handler = SignalHandler("test-app")
    
    # Flag to track if handler was called
    called = {"ok": False}
    
    # Register a cleanup function
    def cleanup():
        called["ok"] = True
    
    # Register the cleanup function for SIGINT
    handler.register_signal_handler(signal.SIGINT, cleanup)
    
    # Initialize the handler
    handler.initialize()
    
    # Simulate calling the handler directly (without actually sending a signal)
    handler._handle_signal(signal.SIGINT, None)
    
    # Verify the cleanup function was called
    assert called["ok"]
    
    # Verify that signal handlers were properly set up
    assert signal.getsignal(signal.SIGINT) is not None
    
    # Clean up
    handler.shutdown()