import pytest
import time
from db_engine import DBEngine

def test_compound_index(tmp_path):
    path = tmp_path / "events.json"
    engine = DBEngine(path=str(path), encryption_key=b'k'*16)
    engine.createIndex(['userID', 'eventType'])
    t = time.time()
    id1 = engine.upsert({'timestamp': t, 'userID': 'a', 'eventType': 'x'})
    id2 = engine.upsert({'timestamp': t, 'userID': 'a', 'eventType': 'y'})
    res = engine.query({'userID': 'a', 'eventType': 'x'})
    assert len(res) == 1 and res[0]['id'] == id1
