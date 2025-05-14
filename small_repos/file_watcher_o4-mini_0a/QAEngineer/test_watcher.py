import pytest
import time
from watcher.watcher import Watcher

def test_detect_changes():
    w = Watcher(paths=[])
    old = {'a': 1, 'b': 2}
    new = {'b': 3, 'c': 4}
    events = w._detect_changes(old, new)
    assert ('a', 'delete') in events
    assert ('b', 'modify') in events
    assert ('c', 'create') in events

def test_filter_and_debounce():
    w = Watcher(paths=[], debounce_interval=0.1, hidden_filter=True)
    assert not w._filter_event('/.hidden')
    assert not w._filter_event('/file~')
    assert w._filter_event('/normal.txt')
    p, e = '/normal.txt', 'modify'
    assert w._should_handle(p, e)
    assert not w._should_handle(p, e)
    time.sleep(0.11)
    assert w._should_handle(p, e)
