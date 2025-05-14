import time
import pytest
from db_engine import DBEngine

def test_ttl_expiry(tmp_path):
    path = tmp_path / "events.json"
    engine = DBEngine(path=str(path), encryption_key=b'k'*16)
    engine.setTTL(1)
    t = time.time()
    eid = engine.upsert({'timestamp': t, 'userID': 'ttl', 'eventType': 'x'})
    # event present immediately
    assert engine.query()[0]['id'] == eid
    time.sleep(1.5)
    assert engine.query() == []
