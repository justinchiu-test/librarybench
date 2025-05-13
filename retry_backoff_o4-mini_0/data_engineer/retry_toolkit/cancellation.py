import threading

class CancelledError(Exception):
    pass

class CancellationPolicy:
    def __init__(self, event: threading.Event):
        self.event = event

    def check_cancel(self):
        if self.event.is_set():
            raise CancelledError("Operation cancelled")
