import os
import time
import tempfile
import shutil
import pytest
from api_startup.db_engine import DBEngine

@pytest.fixture
def tmpdir_db():
    dirpath = tempfile.mkdtemp()
    path = os.path.join(dirpath, 'events.json')
    engine = DBEngine(path=path, encryption_key=b'key123456789012')
    yield engine, path, dirpath
    shutil.rmtree(dirpath)

def test_enforce_schema(tmpdir_db):
    engine, _, _ = tmpdir_db
    with pytest.raises(ValueError):
        engine.upsert({'userID': 'u1', 'eventType': 'click'})
    with pytest.raises(ValueError):
        engine.upsert({'timestamp': 'bad', 'userID': 'u1', 'eventType': 'click'})
    # valid
    eid = engine.upsert({'timestamp': time.time(), 'userID': 'u1', 'eventType': 'click'})
    assert isinstance(eid, int)

def test_persist_atomic(tmpdir_db):
    engine, path, _ = tmpdir_db
    eid = engine.upsert({'timestamp': time.time(), 'userID': 'u2', 'eventType': 'view'})
    assert os.path.exists(path)
    with open(path, 'rb') as f:
        data = f.read()
    # ensure not plaintext JSON
    assert b'"userID"' not in data

def test_batch_upsert_atomic(tmpdir_db):
    engine, path, _ = tmpdir_db
    t = time.time()
    valid = {'timestamp': t, 'userID': 'u3', 'eventType': 'login'}
    invalid = {'timestamp': t, 'userID': 'u3'}  # missing eventType
    with pytest.raises(ValueError):
        engine.batchUpsert([valid, invalid])
    # ensure no events persisted
    res = engine.query()
    assert res == []

def test_indices_and_query(tmpdir_db):
    engine, _, _ = tmpdir_db
    engine.createIndex('userID')
    t = time.time()
    e1 = {'timestamp': t, 'userID': 'alice', 'eventType': 'a'}
    e2 = {'timestamp': t, 'userID': 'bob', 'eventType': 'b'}
    id1 = engine.upsert(e1)
    id2 = engine.upsert(e2)
    res = engine.query({'userID': 'alice'})
    assert len(res) == 1 and res[0]['id'] == id1

def test_soft_and_hard_delete(tmpdir_db):
    engine, _, _ = tmpdir_db
    t = time.time()
    eid = engine.upsert({'timestamp': t, 'userID': 'x', 'eventType': 'e'})
    engine.softDelete(eid)
    res = engine.query()
    assert res == []
    engine.undelete(eid)
    res2 = engine.query()
    assert len(res2) == 1
    engine.delete(id=eid)
    res3 = engine.query()
    assert res3 == []

def test_ttl(tmpdir_db):
    engine, _, _ = tmpdir_db
    engine.setTTL(1)
    t = time.time()
    eid = engine.upsert({'timestamp': t, 'userID': 'ttl', 'eventType': 'e'})
    time.sleep(2)
    res = engine.query()
    assert res == []

def test_plugin_registration(tmpdir_db):
    engine, _, _ = tmpdir_db
    class SamplePlugin:
        def __init__(self):
            self.engines = []
        def register(self, eng):
            self.engines.append(eng)
            self.called = False
        def on_upsert(self, eid, evt):
            self.called = True
    plugin = SamplePlugin()
    engine.registerPlugin(plugin)
    eid = engine.upsert({'timestamp': time.time(), 'userID': 'p', 'eventType': 'e'})
    assert plugin.engines == [engine]
    assert plugin.called

def test_query_nonindexed(tmpdir_db):
    engine, _, _ = tmpdir_db
    t = time.time()
    e1 = {'timestamp': t, 'userID': 'u', 'eventType': 'x'}
    id1 = engine.upsert(e1)
    res = engine.query({'eventType': 'x'})
    assert len(res) == 1 and res[0]['id'] == id1
