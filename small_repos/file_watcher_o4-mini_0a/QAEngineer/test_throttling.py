import pytest
import time
from watcher.watcher import Watcher

def test_debounce_behavior():
    w = Watcher(paths=[], debounce_interval=0.05)
    path, event = 'x', 'create'
    assert w._should_handle(path, event)
    assert not w._should_handle(path, event)
    time.sleep(0.06)
    assert w._should_handle(path, event)
