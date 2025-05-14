import pytest
import time
from db_engine import DBEngine

def test_batch_success_and_rollback(tmp_path):
    path = tmp_path / "events.json"
    engine = DBEngine(path=str(path), encryption_key=b'k'*16)
    t = time.time()
    evts = [
        {'timestamp': t, 'userID': 'u1', 'eventType': 'e1'},
        {'timestamp': t, 'userID': 'u2', 'eventType': 'e2'}
    ]
    ids = engine.batchUpsert(evts)
    assert len(ids) == 2
    # now a faulty batch
    good = {'timestamp': t, 'userID': 'u3', 'eventType': 'e3'}
    bad = {'timestamp': t, 'userID': 123, 'eventType': 'e4'}
    with pytest.raises(ValueError):
        engine.batchUpsert([good, bad])
    all_events = engine.query()
    assert len(all_events) == 2
