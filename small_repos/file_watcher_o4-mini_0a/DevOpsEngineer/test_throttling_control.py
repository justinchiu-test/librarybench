import pytest
from file_watcher.core import FileWatcher

def test_throttle_integration():
    fw = FileWatcher(throttle_rate=1)
    # first event allowed
    ev1 = fw.trigger_event('x', 't')
    assert ev1 is not None
    # immediate second blocked
    ev2 = fw.trigger_event('x', 't')
    assert ev2 is None
