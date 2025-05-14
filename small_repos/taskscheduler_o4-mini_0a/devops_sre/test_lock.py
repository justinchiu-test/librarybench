import threading
import pytest
from scheduler.lock import acquire_distributed_lock

def test_lock_acquire_release():
    with acquire_distributed_lock('testlock'):
        assert True
    with acquire_distributed_lock('testlock'):
        assert True

def test_lock_timeout():
    import scheduler.lock as lk
    lock = threading.Lock()
    lk._locks['timed'] = lock
    lock.acquire()
    with pytest.raises(TimeoutError):
        with acquire_distributed_lock('timed', timeout=0):
            pass
    lock.release()
