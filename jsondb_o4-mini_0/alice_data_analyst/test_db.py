import pytest
import os
import json
from db import Database
from metrics import Metrics
from hooks import Hooks

@pytest.fixture
def db(tmp_path):
    key = b'\x00' * 32
    metrics = Metrics()
    hooks = Hooks()
    return Database(str(tmp_path), key, metrics, hooks)

def test_insert_and_get(db):
    ev = {'campaign': 'camp1', 'timestamp': '2020-01-01T00:00:00'}
    res = db.insert_event(ev)
    assert 'id' in res
    got = db.get_event(res['id'])
    assert got['campaign'] == 'camp1'
    assert got['normalized'] is True
    assert got['deleted'] is False

def test_update_partial(db):
    ev = db.insert_event({'campaign': 'camp', 'field': 'value'})
    id_ = ev['id']
    updated = db.update_event(id_, {'field2': 'value2'})
    assert updated['field'] == 'value'
    assert updated['field2'] == 'value2'
    assert updated['version'] == 2

def test_soft_delete_and_undelete(db):
    ev = db.insert_event({'campaign': 'c'})
    id_ = ev['id']
    assert db.soft_delete(id_) is True
    got = db.get_event(id_)
    assert got['deleted'] is True
    assert db.undelete_event(id_) is True
    got2 = db.get_event(id_)
    assert got2['deleted'] is False

def test_purge_event(db):
    ev = db.insert_event({'campaign': 'c'})
    id_ = ev['id']
    assert db.purge_event(id_) is True
    assert db.get_event(id_) is None
    assert db.get_versions(id_) is None

def test_versioning_and_restore(db):
    ev = db.insert_event({'campaign': 'x', 'a': 1})
    id_ = ev['id']
    db.update_event(id_, {'a': 2})
    db.update_event(id_, {'a': 3})
    vers = db.get_versions(id_)
    assert vers == [1, 2, 3]
    restored = db.restore_version(id_, 1)
    assert restored['a'] == 1
    assert restored['version'] == 4
    vers2 = db.get_versions(id_)
    assert 4 in vers2

def test_query_filters(db):
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    e1 = db.insert_event({'campaign': 'A', 'timestamp': now.isoformat()})
    e2 = db.insert_event({'campaign': 'B', 'timestamp': (now - timedelta(days=1)).isoformat()})
    e3 = db.insert_event({'campaign': 'A', 'timestamp': (now + timedelta(days=1)).isoformat()})
    res = db.query(campaign='A')
    assert len(res) == 2
    start = (now - timedelta(hours=1)).isoformat()
    end = (now + timedelta(hours=1)).isoformat()
    r2 = db.query(None, start, end)
    assert len(r2) == 1 and r2[0]['id'] == e1['id']

def test_batch_upsert_atomic(db):
    events = [{'campaign': 'x'}, {'campaign': 'y'}]
    res = db.batch_upsert(events)
    assert len(res) == 2
    ids = [e['id'] for e in res]
    for id_ in ids:
        assert db.get_event(id_) is not None

def test_encryption_files(db, tmp_path):
    ev = db.insert_event({'campaign': 'c'})
    id_ = ev['id']
    file = tmp_path / 'events' / f"{id_}.json.enc"
    data = file.read_bytes()
    assert id_.encode() not in data

def test_journal_entries(db, tmp_path):
    ev = db.insert_event({'campaign': 'c'})
    id_ = ev['id']
    db.update_event(id_, {'f': 1})
    db.soft_delete(id_)
    journal = tmp_path / 'journal' / 'journal.log'
    lines = journal.read_text().splitlines()
    assert len(lines) == 3
    entries = [json.loads(l) for l in lines]
    assert entries[0]['op'] == 'insert'
    assert entries[1]['op'] == 'update'
    assert entries[2]['op'] == 'soft_delete'
