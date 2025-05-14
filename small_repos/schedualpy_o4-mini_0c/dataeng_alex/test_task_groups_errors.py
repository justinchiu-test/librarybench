import pytest
from scheduler import ThreadSafeScheduler

def test_group_errors():
    scheduler = ThreadSafeScheduler()
    with pytest.raises(KeyError):
        scheduler.pause_group('nonexistent')
    with pytest.raises(KeyError):
        scheduler.resume_group('nonexistent')
    scheduler.create_task_group('g1')
    with pytest.raises(KeyError):
        scheduler.create_task_group('g1')
