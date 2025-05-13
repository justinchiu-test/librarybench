import time
import json
from pathlib import Path
from iotdb.engine import IoTEngine

def test_ingest_and_query():
    eng = IoTEngine()
    t0 = 1000
    eng.ingest('d1', 10, timestamp=t0)
    eng.ingest('d1', 20, timestamp=t0+10)
    res = eng.query(['d1'], t0, t0+10)
    assert res['d1'] == [(t0, 10), (t0+10, 20)]

def test_cache():
    eng = IoTEngine()
    t = 0
    eng.ingest('d1', 1, timestamp=t)
    res1 = eng.query(['d1'], 0, 10, use_cache=True)
    eng.ingest('d1', 2, timestamp=5)
    res2 = eng.query(['d1'], 0, 10, use_cache=True)
    assert res2 == res1
    time.sleep(1)
    res3 = eng.query(['d1'], 0, 10, use_cache=True)
    assert (t, 1) in res3['d1']

def test_transformation():
    def add_offset(device, value, ts, tags):
        return value + 5
    eng = IoTEngine()
    eng.register_transformation(add_offset)
    eng.ingest('d1', 10, timestamp=0)
    res = eng.query(['d1'], 0, 10)
    assert res['d1'][0][1] == 15

def test_detector():
    called = []
    def detect(device, value, ts, tags):
        called.append((device, value))
    eng = IoTEngine()
    eng.register_detector(detect)
    eng.ingest('d1', 7)
    assert called == [('d1', 7)]

def test_snapshot(tmp_path):
    path = tmp_path / 'snap.p'
    eng = IoTEngine(snapshot_path=str(path))
    eng.ingest('d1', 1, timestamp=1)
    eng.snapshot_save()
    eng2 = IoTEngine(snapshot_path=str(path))
    eng2.snapshot_load()
    assert eng2.data == eng.data

def test_import_json(tmp_path):
    data = [{'device_id':'d1','value':100,'timestamp':50,'tags':{'room':'k'}}]
    path = tmp_path / 'd.json'
    path.write_text(json.dumps(data))
    eng = IoTEngine()
    eng.import_json(str(path))
    res = eng.query(['d1'], 0, 100)
    assert res['d1'][0][1] == 100
    assert eng.tags['d1']['room'] == 'k'

def test_replication():
    eng1 = IoTEngine()
    eng2 = IoTEngine()
    eng1.replicate_to(eng2)
    eng1.ingest('d1', 5, timestamp=0)
    assert eng2.data['d1'][0][1] == 5

def test_query_by_tag():
    eng = IoTEngine()
    eng.ingest('d1', 1, timestamp=0, tags={'room':'a'})
    eng.ingest('d2', 2, timestamp=0, tags={'room':'b'})
    res = eng.query_by_tag('room:a', 0, 10)
    assert 'd1' in res and 'd2' not in res

def test_retention_in_engine():
    eng = IoTEngine()
    now = 1000000
    olds = now - 100*24*3600
    eng.data = {'d1': [(olds, 10)]}
    eng.apply_retention(now)
    assert eng.data['d1'] == []

def test_interpolate_engine():
    eng = IoTEngine()
    eng.ingest('d1', 0, timestamp=0)
    eng.ingest('d1', 10, timestamp=10)
    assert eng.interpolate('d1', 5) == 5
