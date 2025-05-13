import pytest
import time
from file_watcher.core import FileWatcher, Event, SymlinkConfig

def test_trigger_event_stores_and_returns_event():
    fw = FileWatcher()
    ev = fw.trigger_event('/path/to/file.txt', 'modify')
    assert isinstance(ev, Event)
    assert ev.path == '/path/to/file.txt'
    assert ev.type == 'modify'
    # event is in history
    hist = fw.store.get_events()
    assert ev in hist

def test_ignore_symlink_paths_when_configured():
    fw = FileWatcher(symlink=SymlinkConfig.IGNORE)
    ev = fw.trigger_event('/some/symlinked/file', 'create')
    assert ev is None

def test_follow_symlink_paths_when_configured():
    fw = FileWatcher(symlink=SymlinkConfig.FOLLOW)
    ev = fw.trigger_event('/some/symlinked/file', 'create')
    assert ev is not None

def test_custom_history_size_rollover():
    fw = FileWatcher(history_max_size=2)
    e1 = fw.trigger_event('/a', 'x')
    e2 = fw.trigger_event('/b', 'x')
    e3 = fw.trigger_event('/c', 'x')
    events = fw.store.get_events()
    assert len(events) == 2
    assert events == [e2, e3]
