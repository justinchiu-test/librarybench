import os
import time
import tempfile
import json
import pytest
from mobile_dev.journaling.db import JournalDB
from mobile_dev.journaling.schema import SchemaError

def make_entry(eid, tags=None):
    now = time.time()
    return {
        'id': eid,
        'content': f'content {eid}',
        'tags': tags or [],
        'attachments': [],
        'metadata': {},
        'created_at': now,
        'updated_at': now
    }

@pytest.fixture
def db(tmp_path):
    key = os.urandom(32)
    return JournalDB(str(tmp_path), key, ttl_days=1)

def test_upsert_and_index(db):
    e1 = make_entry('1', ['t1', 't2'])
    db.upsert(e1)
    assert '1' in db.entries
    assert 't1' in db.index and '1' in db.index['t1']
    assert 't2' in db.index and '1' in db.index['t2']
    # persisted file exists
    fname = os.path.join(db.directory, '1.json.enc')
    assert os.path.exists(fname)

def test_invalid_entry(db):
    with pytest.raises(SchemaError):
        db.upsert({'invalid': 'entry'})

def test_batch_upsert_and_atomic(db):
    e1 = make_entry('b1')
    e2 = make_entry('b2')
    db.batchUpsert([e1, e2])
    assert 'b1' in db.entries and 'b2' in db.entries
    # cause error in batch
    bad = {'id':'b3'}
    with pytest.raises(Exception):
        db.batchUpsert([make_entry('b3'), bad])
    assert 'b3' not in db.entries

def test_delete_and_delete_filter(db):
    e = make_entry('d1', ['draft'])
    db.upsert(e)
    db.delete_by_id('d1')
    assert 'd1' not in db.entries
    e2 = make_entry('d2', ['keep'])
    db.upsert(e2)
    db.delete(lambda ent: 'keep' in ent['tags'])
    assert 'd2' not in db.entries

def test_soft_delete_and_purge(db):
    e = make_entry('s1')
    db.upsert(e)
    db.softDelete('s1')
    assert db.entries['s1'].get('deleted', False)
    db.purge('s1')
    assert 's1' not in db.entries

def test_delete_drafts_older_than(db):
    e = make_entry('old', ['draft'])
    db.upsert(e)
    # make it old
    old = db.entries['old']
    old['created_at'] = time.time() - 2*24*3600
    db.upsert(old)
    db.deleteDraftsOlderThan(1)
    assert 'old' not in db.entries

def test_persist_atomically(tmp_path):
    path = tmp_path / "sub" / "test.enc"
    dbdir = str(tmp_path / "db")
    os.makedirs(dbdir)
    from mobile_dev.journaling.db import JournalDB
    key = os.urandom(32)
    db = JournalDB(dbdir, key)
    data = b'data'
    # use internal method
    db.persistAtomically(str(path), data)
    assert path.exists()
    assert path.read_bytes() == data
