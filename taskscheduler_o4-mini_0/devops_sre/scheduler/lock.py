import threading
from contextlib import contextmanager

_locks = {}

@contextmanager
def acquire_distributed_lock(name, timeout=None):
    lock = _locks.setdefault(name, threading.Lock())
    acquired = lock.acquire(timeout=timeout) if timeout is not None else lock.acquire()
    try:
        if not acquired:
            raise TimeoutError(f"Could not acquire lock {name}")
        yield
    finally:
        if acquired:
            lock.release()
