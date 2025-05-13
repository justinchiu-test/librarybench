import threading

class CancellationPolicy:
    def __init__(self):
        self._event = threading.Event()

    def cancel(self):
        """
        Signal cancellation.
        """
        self._event.set()

    def is_cancelled(self):
        """
        Return True if cancellation has been requested.
        """
        return self._event.is_set()
