import os
import json
import pytest
import tempfile
from db import JSONDB

@pytest.fixture
def tmp_files(tmp_path):
    db_file = tmp_path / "db.json"
    journal_file = tmp_path / "journal.log"
    key = b'0' * 32
    return str(db_file), str(journal_file), key

def test_log_and_query(tmp_files):
    db_file, journal_file, key = tmp_files
    db = JSONDB(db_file, journal_file, key)
    txn = {'account': 'A1', 'amount': 100}
    tid = db.log_transaction(txn)
    res = db.query_by_account('A1')
    assert len(res) == 1
    assert res[0]['id'] == tid
    # journaling
    with open(journal_file) as f:
        lines = f.readlines()
    entries = [json.loads(l) for l in lines]
    assert any(e['action'] == 'log' for e in entries)

def test_encryption(tmp_files):
    db_file, journal_file, key = tmp_files
    db = JSONDB(db_file, journal_file, key)
    db.log_transaction({'account': 'A2', 'amount': 200})
    data = open(db_file, 'rb').read()
    # should not contain plaintext account name
    assert b'A2' not in data
    assert len(data) > 0

def test_update_and_version(tmp_files):
    db_file, journal_file, key = tmp_files
    db = JSONDB(db_file, journal_file, key)
    tid = db.log_transaction({'account': 'A3', 'amount': 300})
    updated = db.update_transaction(tid, {'status': 'reconciled'})
    assert updated['version'] == 2
    res = db.query_by_account('A3')
    assert res[0]['status'] == 'reconciled'

def test_soft_delete(tmp_files):
    db_file, journal_file, key = tmp_files
    db = JSONDB(db_file, journal_file, key)
    tid = db.log_transaction({'account': 'A4', 'amount': 400})
    db.soft_delete(tid)
    res = db.query_by_account('A4')
    assert res == []
    # include_deleted
    res2 = db.query_by_account('A4', include_deleted=True)
    assert any(r['deleted'] for r in res2)

def test_batch_upsert_success(tmp_files):
    db_file, journal_file, key = tmp_files
    db = JSONDB(db_file, journal_file, key)
    txns = [
        {'account': 'B1', 'amount': 10},
        {'account': 'B2', 'amount': 20}
    ]
    ids = db.batch_upsert(txns)
    assert len(ids) == 2
    res1 = db.query_by_account('B1')
    res2 = db.query_by_account('B2')
    assert res1 and res2

def test_batch_upsert_failure_atomic(tmp_files):
    db_file, journal_file, key = tmp_files
    db = JSONDB(db_file, journal_file, key)
    # initial empty
    with pytest.raises(ValueError):
        db.batch_upsert([{'account': 'C1', 'amount': 5}, {'account': 'C2'}])
    # ensure no partial writes
    res = db.query_by_account('C1')
    assert res == []

def test_pre_and_post_hooks(tmp_files):
    db_file, journal_file, key = tmp_files
    calls = {'post': [], 'pre': []}
    def pre_hook(txn):
        calls['pre'].append(txn)
        if txn.get('amount', 0) > 500:
            raise ValueError("AML violation")
    def post_hook(rec):
        calls['post'].append(rec)
    db = JSONDB(db_file, journal_file, key, pre_hooks=[pre_hook], post_hooks=[post_hook])
    # valid
    tid = db.log_transaction({'account': 'D1', 'amount': 100})
    assert calls['pre']
    assert calls['post']
    # invalid
    with pytest.raises(ValueError):
        db.log_transaction({'account': 'D1', 'amount': 600})
    # no second post
    assert len(calls['post']) == 1

def test_metrics(tmp_files):
    db_file, journal_file, key = tmp_files
    db = JSONDB(db_file, journal_file, key)
    assert db.metrics['system_health'] == 1
    # perform ops
    db.log_transaction({'account': 'M1', 'amount': 1})
    db.query_by_account('M1')
    db.update_transaction(db.query_by_account('M1')[0]['id'], {'status': 'x'})
    db.soft_delete(db.query_by_account('M1', include_deleted=True)[0]['id'])
    db.batch_upsert([{'account': 'M2', 'amount': 2}])
    # throughput should equal number of ops (5)
    assert db.metrics['request_throughput'] == 5
    # query_latency has at least one entry
    assert db.metrics['query_latency']
    # index hit ratio non-negative
    assert db.metrics['index_hit_ratio'] >= 0
