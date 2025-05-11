import os
import pytest
from game_service.storage import GameStore

def test_encrypted_file(tmp_path):
    store = GameStore(str(tmp_path), encryption_key='key')
    store.save({'a': 1})
    raw = open(os.path.join(str(tmp_path), 'data.json'), 'rb').read()
    assert b'{' not in raw
    d = store.load()
    assert d == {'a': 1}
