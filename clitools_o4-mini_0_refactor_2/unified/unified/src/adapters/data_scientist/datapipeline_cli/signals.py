"""
Signal handling for data_scientist datapipeline CLI.
"""
import signal

def handle_signals(cleanup):
    def handler(signum, frame):
        cleanup()
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return handler