import os
import pytest
from game_service.storage import GameStore

def test_atomic_write(tmp_path):
    store = GameStore(str(tmp_path))
    store.save({'val': 1})
    p = os.path.join(str(tmp_path), 'data.json')
    assert os.path.exists(p)
    content = open(p).read()
    assert '"val": 1' in content
