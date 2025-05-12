from config_framework.hot_reload import HotReload

class DummyLoader:
    def __init__(self):
        self.called = False
    def load(self):
        self.called = True
        return {'k': 'v'}

def test_hot_reload():
    loader = DummyLoader()
    hr = HotReload(loader)
    calls = []
    hr.watch(lambda cfg: calls.append(cfg))
    cfg = hr.reload()
    assert loader.called
    assert cfg == {'k': 'v'}
    assert calls == [{'k': 'v'}]
