import threading

class CancellationPolicy:
    def __init__(self):
        self._event = threading.Event()

    def cancel(self):
        self._event.set()

    def is_cancelled(self):
        return self._event.is_set()

    def check_cancelled(self):
        if self.is_cancelled():
            raise Exception("Operation cancelled")
