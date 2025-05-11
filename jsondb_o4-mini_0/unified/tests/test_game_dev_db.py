import os
import time
import tempfile
import pytest
from game_dev.jsonschema import ValidationError
from game_dev.db import JSONDB

class DummyPlugin:
    def __init__(self):
        self.events = []
    def after_upsert(self, collection, doc):
        self.events.append((collection, doc))

@pytest.fixture
def tmpdb(tmp_path):
    path = tmp_path / "testdb.json"
    return JSONDB(str(path))

def test_set_ttl_and_expiry(tmpdb):
    tmpdb.setTTL('matches', hours=0)  # immediate expiry
    tmpdb.batchUpsert('matches', [{'id': 'm1', 'score': 10}])
    assert 'm1' not in tmpdb.data['matches']

def test_create_index(tmpdb):
    tmpdb.batchUpsert('players', [{'id': 'p1', 'score': 100}, {'id': 'p2', 'score': 200}])
    tmpdb.createIndex('players', 'score')
    idx = tmpdb.indices['players']['score']
    assert 100 in idx and 'p1' in idx[100]
    assert 200 in idx and 'p2' in idx[200]

def test_encrypt_at_rest(tmpdb):
    key = b'0' * 32
    tmpdb.encryptAtRest(key)
    tmpdb.batchUpsert('players', [{'id': 'p1', 'score': 50}])
    # reload with new instance
    db2 = JSONDB(tmpdb.path)
    db2.encryptAtRest(key)
    # force load
    db2._load()
    assert db2.data['players']['p1']['score'] == 50

def test_enforce_schema(tmpdb):
    schema = {'type': 'object', 'properties': {'id': {'type': 'string'}, 'name': {'type': 'string'}}, 'required': ['id','name']}
    tmpdb.enforceSchema('players', schema)
    with pytest.raises(ValidationError):
        tmpdb.batchUpsert('players', [{'id': 'p1'}])  # missing name

def test_register_plugin(tmpdb):
    plugin = DummyPlugin()
    tmpdb.registerPlugin(plugin)
    tmpdb.batchUpsert('players', [{'id': 'p1', 'score': 5}])
    assert plugin.events[0][0] == 'players'
    assert plugin.events[0][1]['id'] == 'p1'

def test_batch_upsert_and_persist(tmpdb):
    tmpdb.batchUpsert('players', [{'id': 'p1', 'score': 10}, {'id': 'p2', 'score': 20}])
    assert os.path.exists(tmpdb.path)
    db2 = JSONDB(tmpdb.path)
    assert 'p1' in db2.data['players'] and db2.data['players']['p2']['score'] == 20

def test_delete_and_soft_delete(tmpdb):
    tmpdb.batchUpsert('players', [{'id': 'p1', 'score': 10}, {'id': 'p2', 'score': 20}])
    tmpdb.softDelete('players', filter={'score': 10})
    assert tmpdb.data['players']['p1']['deleted']
    tmpdb.delete('players', _id='p2')
    assert 'p2' not in tmpdb.data['players']

def test_persist_atomically(tmpdb):
    tmpdb.batchUpsert('players', [{'id': 'p1', 'score': 1}])
    # Simulate atomic persist
    tmpdb.persistAtomically()
    with open(tmpdb.path, 'r') as f:
        raw = f.read()
    assert '"p1"' in raw

def test_rest_server(tmpdb):
    tmpdb.batchUpsert('players', [{'id': 'p1', 'score': 100}])
    tmpdb.enforceSchema('players', {'type':'object','properties':{'id':{'type':'string'},'score':{'type':'number'}},'required':['id','score']})
    tmpdb.startRestServer(host='127.0.0.1', port=5001)
    time.sleep(1)
    from requests import get, post, delete
    # GET
    r = get('http://127.0.0.1:5001/players')
    assert r.status_code == 200 and 'p1' in r.json()
    # POST valid
    r = post('http://127.0.0.1:5001/players', json={'id':'p2','score':50})
    assert r.status_code == 201
    # POST invalid
    r = post('http://127.0.0.1:5001/players', json={'id':'p3'})
    assert r.status_code == 400
    # DELETE soft
    r = delete('http://127.0.0.1:5001/players/p2?soft=1')
    assert r.status_code == 200
    # DELETE hard
    r = delete('http://127.0.0.1:5001/players/p2')
    assert r.status_code == 200
