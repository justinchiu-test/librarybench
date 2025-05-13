import pytest
from file_watcher.core import FileWatcher

def test_handler_invoked_on_matching_event():
    fw = FileWatcher()
    called = []
    def cb(ev):
        called.append(ev)
    fw.register_handler('create', r'.*\.cfg$', cb)
    fw.trigger_event('foo.cfg', 'create')
    fw.trigger_event('foo.txt', 'create')
    assert len(called) == 1
    assert called[0].path == 'foo.cfg'

def test_wildcard_event_type():
    fw = FileWatcher()
    called = []
    def cb(ev):
        called.append(ev)
    fw.register_handler('*', r'.*', cb)
    fw.trigger_event('any', 'random')
    assert len(called) == 1
