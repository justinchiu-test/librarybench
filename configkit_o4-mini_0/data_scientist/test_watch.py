import time
from config.watch import ConfigWatcher, HotReload

def test_config_watcher(tmp_path):
    file = tmp_path / 'cfg.txt'
    file.write_text('a')
    called = []
    def cb(path):
        called.append(path)
    watcher = ConfigWatcher()
    watcher.add_watch(str(file), cb)
    watcher.start()
    time.sleep(0.2)
    file.write_text('b')
    time.sleep(0.2)
    watcher.stop()
    assert called, "Callback was not called"
    assert called[0] == str(file)

def test_hot_reload_is_subclass():
    hr = HotReload()
    assert isinstance(hr, ConfigWatcher)
