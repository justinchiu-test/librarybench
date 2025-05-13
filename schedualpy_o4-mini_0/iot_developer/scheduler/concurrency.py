import threading

class ConcurrencyLimiter:
    def __init__(self, limit):
        self._sem = threading.Semaphore(limit)

    def acquire(self):
        self._sem.acquire()

    def release(self):
        self._sem.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
