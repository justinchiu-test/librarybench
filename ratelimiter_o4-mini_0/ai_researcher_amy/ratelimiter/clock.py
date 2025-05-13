import time

class MockableClock:
    def __init__(self):
        self._offset = 0.0

    def now(self):
        return time.monotonic() + self._offset

    def advance(self, seconds):
        self._offset += seconds
