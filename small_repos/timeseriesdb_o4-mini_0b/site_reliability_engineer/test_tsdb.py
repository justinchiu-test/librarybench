import os
import time
import json
import pickle
import pytest
from tsdb.tsdb import TimeSeriesDB

def test_insert_and_query():
    db = TimeSeriesDB(wal_path='test_wal.log', snapshot_path='test_snapshot.pkl', cache_ttl=5)
    rec = {'name': 'cpu', 'timestamp': 1, 'value': 10, 'tags': {'host': 'a'}}
    db.insert(rec)
    rec2 = {'name': 'cpu', 'timestamp': 2, 'value': 20, 'tags': {'host': 'a'}}
    db.insert(rec2)
    assert db.query('cpu', 0, 10) == [10, 20]
    assert db.query('cpu', 0, 10, agg='sum') == 30
    assert db.query('cpu', 0, 10, agg='avg') == 15
    assert db.query('cpu', 0, 10, agg='p95') == 20
    # cleanup
    os.remove('test_wal.log')
    if os.path.exists('test_snapshot.pkl'):
        os.remove('test_snapshot.pkl')

def test_query_cache_hits_and_misses():
    db = TimeSeriesDB(wal_path='wc_wal.log', snapshot_path='wc_snap.pkl', cache_ttl=5)
    rec = {'name': 'mem', 'timestamp': 1, 'value': 5, 'tags': {}}
    db.insert(rec)
    # first query -> miss
    _ = db.query('mem', 0, 2, agg='sum')
    # second query same -> hit
    _ = db.query('mem', 0, 2, agg='sum')
    assert db.cache.hits == 1
    assert db.cache.misses >= 1
    os.remove('wc_wal.log')
    if os.path.exists('wc_snap.pkl'):
        os.remove('wc_snap.pkl')

def test_wal_replay(tmp_path):
    wal = tmp_path / "wal.log"
    snap = tmp_path / "snap.pkl"
    db1 = TimeSeriesDB(wal_path=str(wal), snapshot_path=str(snap))
    rec = {'name': 'net', 'timestamp': 5, 'value': 100, 'tags': {}}
    db1.insert(rec)
    # create new db, should replay wal
    db2 = TimeSeriesDB(wal_path=str(wal), snapshot_path=str(snap))
    res = db2.query('net', 0, 10)
    assert res == [100]

def test_snapshot_and_load(tmp_path):
    wal = tmp_path / "w2.log"
    snap = tmp_path / "s2.pkl"
    db1 = TimeSeriesDB(wal_path=str(wal), snapshot_path=str(snap))
    rec = {'name': 'disk', 'timestamp': 10, 'value': 300, 'tags': {}}
    db1.insert(rec)
    db1.snapshot_now()
    # clear wal file to ensure load from snapshot
    open(str(wal), 'w').close()
    db2 = TimeSeriesDB(wal_path=str(wal), snapshot_path=str(snap))
    assert db2.query('disk', 0, 20) == [300]

def test_anomaly_detector():
    db = TimeSeriesDB(wal_path='a.log', snapshot_path='a.pkl')
    # flag if value > 50
    db.register_anomaly_hook(lambda r: r['value'] > 50)
    db.insert({'name': 'x', 'timestamp': 1, 'value': 10, 'tags': {}})
    db.insert({'name': 'x', 'timestamp': 2, 'value': 100, 'tags': {}})
    assert len(db.anomaly.anomalies) == 1
    os.remove('a.log')
    if os.path.exists('a.pkl'):
        os.remove('a.pkl')

def test_json_import(tmp_path):
    path = tmp_path / "data.json"
    data = [
        {'name': 'y', 'timestamp': 1, 'value': 1, 'tags': {}},
        {'name': 'y', 'timestamp': 2, 'value': 2, 'tags': {}}
    ]
    with open(str(path), 'w') as f:
        json.dump(data, f)
    db = TimeSeriesDB(wal_path=str(tmp_path/'jwal.log'), snapshot_path=str(tmp_path/'jsnap.pkl'))
    db.import_json(str(path))
    assert db.query('y', 0, 10) == [1, 2]

def test_cluster_replication():
    db1 = TimeSeriesDB(wal_path='c1.log', snapshot_path='c1.pkl')
    db2 = TimeSeriesDB(wal_path='c2.log', snapshot_path='c2.pkl')
    db1.add_cluster_peer(db2)
    rec = {'name': 'z', 'timestamp': 3, 'value': 50, 'tags': {}}
    db1.insert(rec)
    assert db2.query('z', 0, 10) == [50]
    for f in ['c1.log','c1.pkl','c2.log','c2.pkl']:
        if os.path.exists(f):
            os.remove(f)

def test_tag_pattern_query():
    db = TimeSeriesDB(wal_path='t.log', snapshot_path='t.pkl')
    rec1 = {'name': 'm', 'timestamp': 1, 'value': 1, 'tags': {'env': 'prod1'}}
    rec2 = {'name': 'm', 'timestamp': 2, 'value': 2, 'tags': {'env': 'dev'}}
    db.insert(rec1)
    db.insert(rec2)
    matches = db.query_tags('env:prod*')
    # keys are tuples (name, frozenset)
    assert any('prod1' in dict(k[1]).get('env','') for k in matches)
    assert all(dict(k[1]).get('env') != 'dev' for k in matches)
    for f in ['t.log','t.pkl']:
        if os.path.exists(f):
            os.remove(f)

def test_retention_policy():
    now = time.time()
    # set retention: keep 10s, delete beyond
    retention_map = [(10, 'keep'), (float('inf'), 'delete')]
    db = TimeSeriesDB(wal_path='r.log', snapshot_path='r.pkl', retention_map=retention_map)
    # old record
    db.insert({'name': 'old', 'timestamp': now-20, 'value': 1, 'tags': {}})
    # new record
    db.insert({'name': 'new', 'timestamp': now, 'value': 2, 'tags': {}})
    # enforce called on insert, so storage updated
    assert any(k[0]=='new' for k in db.storage)
    assert all(k[0]!='old' for k in db.storage)
    for f in ['r.log','r.pkl']:
        if os.path.exists(f):
            os.remove(f)

def test_transformation_hook():
    db = TimeSeriesDB(wal_path='tr.log', snapshot_path='tr.pkl')
    # multiply value by 2
    db.register_transform_hook(lambda r: {'name':r['name'],'timestamp':r['timestamp'],'value':r['value']*2,'tags':r['tags']})
    db.insert({'name': 'p', 'timestamp': 1, 'value': 3, 'tags': {}})
    assert db.query('p', 0, 10) == [6]
    for f in ['tr.log','tr.pkl']:
        if os.path.exists(f):
            os.remove(f)

def test_interpolation_methods():
    db = TimeSeriesDB(wal_path='i.log', snapshot_path='i.pkl')
    recs = {'name':'int','timestamp':0,'value':0,'tags':{}}
    db.insert(recs)
    recs2 = {'name':'int','timestamp':10,'value':10,'tags':{}}
    db.insert(recs2)
    key = list(db.storage.keys())[0]
    lin = db.interpolate(key, 0, 10, 5, method='linear')
    assert lin == [(0,0),(5,5.0),(10,10)]
    step = db.interpolate(key, 0, 10, 5, method='step')
    assert step == [(0,0),(5,0),(10,10)]
    for f in ['i.log','i.pkl']:
        if os.path.exists(f):
            os.remove(f)
