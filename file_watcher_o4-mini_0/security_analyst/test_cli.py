import sys
from config_watcher.cli import main

def test_cli_initialization(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['prog', '/tmp', '--webhook-url', 'http://x'])
    called = {'init': False, 'start': False}
    class DummyWatcher:
        def __init__(self, *args, **kwargs):
            called['init'] = True
        async def start(self):
            called['start'] = True
            raise KeyboardInterrupt
    monkeypatch.setattr('config_watcher.cli.ConfigWatcher', DummyWatcher)
    main()
    assert called['init']
    assert called['start']
