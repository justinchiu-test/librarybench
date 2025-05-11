import pytest
from charlie_game_dev.game_service.storage import GameStore

@pytest.fixture
def store(tmp_path):
    return GameStore(str(tmp_path), enable_journal=True)

def test_journaling(store):
    store.update_item('p1', {'x': 1})
    ops = store.journal.replay()
    assert len(ops) == 1
    assert ops[0]['data']['p1']['x'] == 1
