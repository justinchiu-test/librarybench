def test_hot_reload():
    from config.watcher import HotReload
    called = []
    def cb(path):
        called.append(path)
    hr = HotReload()
    hr.watch('/tmp/config.toml', cb)
    hr.simulate_change('/tmp/config.toml')
    assert '/tmp/config.toml' in called
