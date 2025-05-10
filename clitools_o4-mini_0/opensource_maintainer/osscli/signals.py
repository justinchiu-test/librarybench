import signal
import logging

_logger = logging.getLogger(__name__)

def handle_signals(command_name):
    def handler(signum, frame):
        _logger.info(f"Received signal {signum} in command {command_name}, cleaning up")
        print(f"Cleanup after {command_name}")
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return handler
