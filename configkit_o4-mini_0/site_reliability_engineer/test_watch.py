import pytest
from srectl.watch import ConfigWatcher, HotReload

def test_config_watcher():
    watcher = ConfigWatcher()
    called = {}

    def callback(x=None):
        called['x'] = x

    watcher.register('event1', callback)
    watcher.notify('event1', x=42)
    assert called.get('x') == 42

def test_hot_reload():
    paths = ['file1', 'file2']
    called = []

    def cb(path):
        called.append(path)

    hot = HotReload(paths, cb)
    hot.simulate_change('file1')
    hot.simulate_change('unknown')
    assert called == ['file1']
