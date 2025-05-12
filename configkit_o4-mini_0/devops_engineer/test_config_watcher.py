from config_framework.config_watcher import ConfigWatcher

def test_watcher():
    initial = {'a': 1, 'b': 2}
    cw = ConfigWatcher(initial)
    calls = []
    def handler(key, old, new):
        calls.append((key, old, new))
    cw.register('a', handler)
    new_cfg = {'a': 3, 'b': 2}
    cw.update(new_cfg)
    assert calls == [('a', 1, 3)]
    calls.clear()
    cw.update(new_cfg)
    assert calls == []
