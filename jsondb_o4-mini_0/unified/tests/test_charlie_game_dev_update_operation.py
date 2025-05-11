import pytest
from charlie_game_dev.game_service.storage import GameStore

@pytest.fixture
def store(tmp_path):
    return GameStore(str(tmp_path))

def test_update_item(store):
    store.update_item('p1', {'score': 10})
    assert store.load()['p1']['score'] == 10
    store.update_item('p1', {'level': 3})
    d = store.load()['p1']
    assert d['score'] == 10 and d['level'] == 3
