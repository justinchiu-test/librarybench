import os
import pytest
from charlie_game_dev.game_service.storage import GameStore

@pytest.fixture
def tmp_store(tmp_path):
    return GameStore(str(tmp_path), encryption_key=None, enable_journal=False)

def test_save_and_load(tmp_store):
    data = {'player1': {'score': 10}}
    tmp_store.save(data)
    loaded = tmp_store.load()
    assert loaded == data

def test_versioning(tmp_store):
    d1 = {'a': 1}
    tmp_store.save(d1)
    d2 = {'b': 2}
    tmp_store.save(d2)
    ver_files = os.listdir(tmp_store.versions_dir)
    assert set(ver_files) == {'1.json', '2.json'}
    assert tmp_store.revert(1)
    assert tmp_store.load() == d1
    assert not tmp_store.revert(99)
