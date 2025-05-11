import pytest
from charlie_game_dev.game_service.storage import GameStore
from charlie_game_dev.game_service.hooks import hooks

@pytest.fixture(autouse=True)
def clear_hooks():
    hooks.pre_write = []
    hooks.post_write = []
    yield

def test_pre_hook(tmp_path):
    store = GameStore(str(tmp_path))
    def pre(data):
        data['new'] = 123
        return data
    hooks.register_pre(pre)
    store.save({'x': 1})
    d = store.load()
    assert d['new'] == 123

def test_post_hook(tmp_path):
    store = GameStore(str(tmp_path))
    called = []
    def post(data):
        called.append(data)
    hooks.register_post(post)
    store.save({'z': 5})
    assert len(called) == 1
    assert called[0]['z'] == 5
