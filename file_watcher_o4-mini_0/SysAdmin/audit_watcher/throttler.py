import time

class Throttler:
    """
    Simple throttler limiting to a number of events per second.
    """
    def __init__(self, limit_per_second: int):
        self.limit = limit_per_second
        self._count = 0
        self._last_reset = 0.0

    def allow(self) -> bool:
        now = time.time()
        # reset the counter if more than one second has passed
        if now - self._last_reset >= 1.0:
            self._count = 0
            self._last_reset = now
        if self._count < self.limit:
            self._count += 1
            return True
        return False
