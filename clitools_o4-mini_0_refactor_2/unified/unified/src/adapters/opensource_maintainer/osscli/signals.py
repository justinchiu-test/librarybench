"""
Signal registration for Open Source Maintainer CLI.
Registers cleanup handler.
"""
import signal

def handle_signals(cmd_name):
    def handler(signum, frame):
        print(f"Cleanup after {cmd_name}")
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    return handler