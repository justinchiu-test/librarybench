import pytest
from scheduler import ThreadSafeScheduler

def test_reschedule_nonexistent():
    scheduler = ThreadSafeScheduler()
    with pytest.raises(KeyError):
        scheduler.reschedule('nojob', 5)

def test_cancel_nonexistent():
    scheduler = ThreadSafeScheduler()
    with pytest.raises(KeyError):
        scheduler.cancel('nojob')
