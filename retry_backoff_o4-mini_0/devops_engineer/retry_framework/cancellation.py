import threading

class CancellationPolicy:
    def __init__(self):
        self.event = threading.Event()

    def cancel(self):
        self.event.set()

    def is_cancelled(self):
        return self.event.is_set()
