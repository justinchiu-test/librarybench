import pytest
import datetime
import json
from platform import TSPlatform

def test_ingest_and_wal():
    ts = TSPlatform()
    now = datetime.datetime.utcnow()
    reading = ts.ingest_reading(now, 500, unit='W', tags={'site': 'alpha'})
    assert reading['value'] == 500
    assert ts.wal and ts.wal[-1]['value'] == 500
    assert ts.data and ts.data[-1]['value'] == 500

def test_transformation_hook():
    ts = TSPlatform()
    now = datetime.datetime.utcnow()
    r1 = ts.ingest_reading(now, 2000, unit='W')
    assert pytest.approx(r1['value_kW'], 0.0001) == 2.0
    r2 = ts.ingest_reading(now, 100, unit='W', power=100, voltage=10, current=5)
    # power_factor = 100 / (10*5) = 2.0
    assert pytest.approx(r2['power_factor'], 0.0001) == 2.0

def test_anomaly_detector():
    ts = TSPlatform()
    now = datetime.datetime.utcnow()
    ts.ingest_reading(now, 100)
    # next reading jumps by 200 (> threshold 50)
    r2 = ts.ingest_reading(now + datetime.timedelta(seconds=1), 300)
    assert r2.get('anomaly', False) is True
    # small jump not anomaly
    r3 = ts.ingest_reading(now + datetime.timedelta(seconds=2), 310)
    assert r3.get('anomaly', False) is False

def test_snapshot_and_restore():
    ts = TSPlatform()
    now = datetime.datetime.utcnow()
    ts.ingest_reading(now, 10)
    snap = ts.snapshot()
    ts.ingest_reading(now + datetime.timedelta(seconds=1), 20)
    assert len(ts.data) == 2
    ts.restore(snap)
    assert len(ts.data) == 1
    assert ts.data[0]['value'] == 10

def test_query_cache():
    ts = TSPlatform()
    calls = {'count': 0}
    def compute():
        calls['count'] += 1
        return 'result'
    # first time
    res1 = ts.query_cache('q1', compute)
    assert res1 == 'result'
    assert calls['count'] == 1
    # second time should be cached
    res2 = ts.query_cache('q1', compute)
    assert res2 == 'result'
    assert calls['count'] == 1

def test_json_import():
    ts = TSPlatform()
    data = [
        {'timestamp': '2023-01-01T00:00:00', 'value': 100, 'unit': 'W', 'tags': {'site':'beta'}},
        {'timestamp': '2023-01-01T00:00:01', 'value': 200, 'unit': 'W', 'tags': {'site':'beta'}}
    ]
    js = json.dumps(data)
    ts.json_import(js)
    assert len(ts.data) == 2
    assert ts.data[0]['tags']['site'] == 'beta'

def test_replicate():
    ts1 = TSPlatform()
    ts2 = TSPlatform()
    now = datetime.datetime.utcnow()
    ts1.ingest_reading(now, 1, tags={'a':'x'})
    ts1.ingest_reading(now + datetime.timedelta(seconds=1), 2, tags={'a':'y'})
    ts1.cache['foo'] = 'bar'
    ts1.replicate(ts2)
    assert len(ts2.data) == 2
    assert ts2.cache.get('foo') == 'bar'
    assert ts2.wal and ts2.wal[0]['value'] == 1

def test_query_by_tag():
    ts = TSPlatform()
    now = datetime.datetime.utcnow()
    ts.ingest_reading(now, 10, tags={'site':'alpha1'})
    ts.ingest_reading(now + datetime.timedelta(seconds=1), 20, tags={'site':'alpha2'})
    ts.ingest_reading(now + datetime.timedelta(seconds=2), 30, tags={'site':'beta'})
    res = ts.query_by_tag('site:alpha*')
    assert len(res) == 2
    res2 = ts.query_by_tag('site:?eta')
    assert len(res2) == 1
    assert res2[0]['tags']['site'] == 'beta'

def test_retention_cleanup():
    ts = TSPlatform()
    now = datetime.datetime.utcnow()
    old = now - datetime.timedelta(days=8)
    ts.ingest_reading(old, 50)
    ts.ingest_reading(now, 60)
    ts.retention_cleanup(now)
    # old reading should be gone
    assert all(r['timestamp'] >= now - datetime.timedelta(days=7) for r in ts.data)
    # current remains
    assert any(r['value'] == 60 for r in ts.data)

def test_interpolation_step_and_spline():
    ts = TSPlatform()
    base = datetime.datetime(2023,1,1,0,0,0)
    ts.ingest_reading(base, 0)
    ts.ingest_reading(base + datetime.timedelta(seconds=4), 4)
    # step interpolation
    step = ts.interpolate(base, base + datetime.timedelta(seconds=4), method='step')
    assert len(step) == 5
    assert [p['value'] for p in step] == [0,0,0,0,4]
    # spline (linear)
    lin = ts.interpolate(base, base + datetime.timedelta(seconds=4), method='spline')
    assert [round(p['value'],1) for p in lin] == [0.0,1.0,2.0,3.0,4.0]

def test_minute_and_daily_summary():
    ts = TSPlatform()
    now = datetime.datetime(2023,5,1,12,34,56)
    ts.ingest_reading(now, 5)
    ts.ingest_reading(now + datetime.timedelta(seconds=5), 10)
    minute = now.replace(second=0, microsecond=0)
    day = now.date()
    assert minute in ts.minute_summary
    assert ts.minute_summary[minute] == [5,10]
    assert day in ts.daily_summary
    assert ts.daily_summary[day] == [5,10]
