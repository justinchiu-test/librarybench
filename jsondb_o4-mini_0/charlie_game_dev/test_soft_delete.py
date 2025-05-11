import pytest
from game_service.storage import GameStore

@pytest.fixture
def store(tmp_path):
    return GameStore(str(tmp_path))

def test_soft_delete_and_undelete(store):
    store.update_item('q1', {'state': 'active'})
    store.soft_delete('q1')
    assert store.load()['q1']['deleted'] is True
    store.undelete('q1')
    assert store.load()['q1']['deleted'] is False
