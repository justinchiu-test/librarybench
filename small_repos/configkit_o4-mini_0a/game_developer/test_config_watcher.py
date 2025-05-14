def test_config_watcher():
    from config.watcher import ConfigWatcher
    called = {}
    def cb(val):
        called['v'] = val
    w = ConfigWatcher()
    w.register('graphics', cb)
    w.update('graphics', 'on')
    assert called.get('v') == 'on'
