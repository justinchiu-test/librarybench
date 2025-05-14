import time

class MockableClock:
    def __init__(self, start=None):
        self._start = start if start is not None else time.time()
        self._offset = 0.0

    def now(self):
        return self._start + self._offset

    def advance(self, seconds):
        self._offset += seconds
