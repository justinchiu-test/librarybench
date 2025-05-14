import threading
class DummyLock:
    def __init__(self, name, timeout=None):
        self._lock = threading.RLock()
    def __enter__(self):
        self._lock.acquire()
        return self
    def __exit__(self, exc_type, exc, tb):
        self._lock.release()

def acquire_distributed_lock(name, timeout=None):
    return DummyLock(name, timeout)
