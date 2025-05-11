import os
import time
import tempfile
import json
import threading
import urllib.request
import pytest
from data_scientist.store import ExperimentStore
from data_scientist.jsonschema import ValidationError

def test_batch_upsert_and_query():
    tmp = tempfile.mkdtemp()
    store = ExperimentStore(tmp)
    store.createIndex('a', 'b')
    recs = [{'parameters': {'a': 1, 'b': 2}, 'results': {'x': 10}},
            {'parameters': {'a': 1, 'b': 3}, 'results': {'x': 20}}]
    inserted = store.batchUpsert(recs)
    assert len(inserted) == 2
    res = store.queryByParams(a=1, b=2)
    assert len(res) == 1
    assert res[0]['results']['x'] == 10

def test_ttl_expiration():
    tmp = tempfile.mkdtemp()
    store = ExperimentStore(tmp)
    store.setTTL(1)
    rec = {'parameters': {'a': 5}, 'results': {}}
    inserted = store.batchUpsert([rec])
    eid = inserted[0]['experiment_id']
    time.sleep(2)
    res = store.queryByParams(a=5)
    assert not res

def test_encryption_and_load():
    tmp = tempfile.mkdtemp()
    key = secrets = os.urandom(32)
    store = ExperimentStore(tmp, encryption_key=key)
    rec = {'parameters': {'p': 'v'}, 'results': {'r': 1}}
    inserted = store.batchUpsert([rec])
    store.persistAtomically('data.bin')
    data = store.load('data.bin')
    assert isinstance(data, list)
    assert data[0]['parameters']['p'] == 'v'
    # ensure file on disk is not plaintext JSON
    raw = open(os.path.join(tmp, 'data.bin'), 'rb').read()
    assert b'parameters' not in raw

def test_schema_enforce():
    tmp = tempfile.mkdtemp()
    schema = {
        "type": "object",
        "properties": {
            "parameters": {"type": "object"},
            "results": {"type": "object"}
        },
        "required": ["parameters", "results"]
    }
    store = ExperimentStore(tmp, schema=schema)
    good = {'parameters': {}, 'results': {}}
    store.batchUpsert([good])
    bad = {'parameters': {}}
    with pytest.raises(ValidationError):
        store.batchUpsert([bad])

def test_plugins():
    tmp = tempfile.mkdtemp()
    store = ExperimentStore(tmp)
    def plugin(entry):
        entry['parameters']['added'] = True
    store.registerPlugin('add', plugin)
    rec = {'parameters': {}, 'results': {}}
    result = store.batchUpsert([rec])[0]
    assert result['parameters']['added'] is True

def test_delete_and_filter():
    tmp = tempfile.mkdtemp()
    store = ExperimentStore(tmp)
    recs = [{'parameters': {'v': 1}, 'results': {}},
            {'parameters': {'v': 2}, 'results': {}}]
    inserted = store.batchUpsert(recs)
    eid0 = inserted[0]['experiment_id']
    store.delete(experiment_id=eid0)
    res = store.queryByParams(v=1)
    assert not res
    # filter delete
    store.delete(filter_func=lambda r: r['parameters']['v'] == 2)
    res2 = store.queryByParams(v=2)
    assert not res2

def test_soft_delete():
    tmp = tempfile.mkdtemp()
    store = ExperimentStore(tmp)
    rec = {'parameters': {'x': 9}, 'results': {}}
    eid = store.batchUpsert([rec])[0]['experiment_id']
    store.softDelete(eid)
    recs = store.queryByParams(x=9)
    assert recs[0]['retired'] is True

def test_persist_nonencrypted():
    tmp = tempfile.mkdtemp()
    store = ExperimentStore(tmp)
    rec = {'parameters': {'k': 'v'}, 'results': {}}
    store.batchUpsert([rec])
    store.persistAtomically('plain.json')
    data = json.loads(open(os.path.join(tmp, 'plain.json')).read())
    assert data[0]['parameters']['k'] == 'v'

def test_rest_server():
    tmp = tempfile.mkdtemp()
    store = ExperimentStore(tmp)
    store.createIndex('q',)
    rec = {'parameters': {'q': 'test'}, 'results': {'out': 5}}
    store.batchUpsert([rec])
    server = store.startRestServer(host='localhost', port=0)
    port = server.server_address[1]
    url = f'http://localhost:{port}/runs?q=test'
    resp = urllib.request.urlopen(url)
    body = resp.read().decode()
    data = json.loads(body)
    assert len(data) == 1
    assert data[0]['results']['out'] == 5
    server.shutdown()
