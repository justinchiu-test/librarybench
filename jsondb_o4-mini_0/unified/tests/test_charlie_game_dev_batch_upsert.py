import pytest
from charlie_game_dev.game_service.storage import GameStore

@pytest.fixture
def store(tmp_path):
    return GameStore(str(tmp_path))

def test_batch_upsert(store):
    items = [{'id': 'p1', 'score': 5}, {'id': 'p2', 'score': 7}]
    store.batch_upsert(items)
    data = store.load()
    assert data['p1']['score'] == 5
    assert data['p2']['score'] == 7
    store.batch_upsert([{'id': 'p1', 'level': 2}])
    data2 = store.load()
    assert data2['p1']['score'] == 5
    assert data2['p1']['level'] == 2
