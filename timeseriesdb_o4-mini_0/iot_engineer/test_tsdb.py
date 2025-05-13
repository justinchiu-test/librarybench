import io
import time
import datetime
import pytest
import tsdb

@pytest.fixture(autouse=True)
def reset_globals():
    tsdb.series_data.clear()
    tsdb.versions.clear()
    tsdb.alert_rules.clear()
    tsdb.alert_events.clear()
    tsdb.cache_data.clear()
    tsdb.cardinality_limits.clear()
    tsdb.series_tag_keys.clear()
    yield
    tsdb.series_data.clear()
    tsdb.versions.clear()
    tsdb.alert_rules.clear()
    tsdb.alert_events.clear()
    tsdb.cache_data.clear()
    tsdb.cardinality_limits.clear()
    tsdb.series_tag_keys.clear()

def test_record_version_and_versions():
    ts = datetime.datetime(2021,1,1,0,0)
    payload = {'value': 10, 'tags': {'a': 'b'}}
    tsdb.record_version('s1', ts, payload, 'ua')
    assert 's1' in tsdb.series_data
    assert tsdb.series_data['s1'][0]['value'] == 10
    assert tsdb.versions[-1]['user_agent'] == 'ua'

def test_cardinality_limit():
    tsdb.enforce_cardinality_limit('s1', 1)
    ts = datetime.datetime.now()
    tsdb.record_version('s1', ts, {'value':1, 'tags':{'a':1}}, 'ua')
    tsdb.record_version('s1', ts, {'value':2, 'tags':{'a':2}}, 'ua')
    with pytest.raises(Exception):
        tsdb.record_version('s1', ts, {'value':3, 'tags':{'b':3}}, 'ua')

def test_export_csv():
    t1 = datetime.datetime(2021,1,1,0,0)
    t2 = datetime.datetime(2021,1,1,1,0)
    tsdb.record_version('s1', t1, {'value':1, 'tags':{'k':'v'}}, 'ua')
    tsdb.record_version('s2', t2, {'value':2, 'tags':{'k':'w'}}, 'ua')
    csv_str = tsdb.export_csv(['s1','s2'], t1 - datetime.timedelta(minutes=1), t2 + datetime.timedelta(minutes=1), True)
    lines = csv_str.split('\n')
    assert lines[0].split(',') == ['series_id','timestamp','value','k']
    rows = lines[1:]
    assert any('s1' in r and '1' in r for r in rows)
    assert any('s2' in r and '2' in r for r in rows)

def test_define_alert_and_trigger():
    tsdb.define_alert('r1', 's1', 'gt', 10, 'url1')
    t = datetime.datetime(2021,1,1,0,0)
    tsdb.record_version('s1', t, {'value': 5, 'tags':{}}, 'ua')
    assert len(tsdb.alert_events) == 0
    tsdb.record_version('s1', t, {'value': 15, 'tags':{}}, 'ua')
    assert len(tsdb.alert_events) == 1
    evt = tsdb.alert_events[0]
    assert evt['rule_id'] == 'r1' and evt['value'] == 15

def test_convert_timezone():
    query = {
        'from_ts': datetime.datetime(2021,1,1,12,0),
        'to_ts': datetime.datetime(2021,1,1,13,0)
    }
    res = tsdb.convert_timezone(query, 'America/New_York')
    # UTC is +5h on Jan 1 in New York
    assert res['from_ts_utc'].hour == 17
    assert res['to_ts_utc'].hour == 18

def test_join_series():
    m = [
        {'timestamp':1, 'value':'m1'},
        {'timestamp':2, 'value':'m2'}
    ]
    a = [
        {'timestamp':2, 'value':'a2'},
        {'timestamp':3, 'value':'a3'}
    ]
    inner = tsdb.join_series(m,a,'inner')
    assert len(inner) == 1 and inner[0]['timestamp']==2
    left = tsdb.join_series(m,a,'left')
    assert len(left) == 2 and {e['timestamp'] for e in left}=={1,2}
    outer = tsdb.join_series(m,a,'outer')
    assert len(outer) == 3 and {e['timestamp'] for e in outer}=={1,2,3}
    with pytest.raises(ValueError):
        tsdb.join_series(m,a,'bad')

def test_stream_data():
    t1 = datetime.datetime(2021,1,1,0,0)
    tsdb.record_version('s1', t1, {'value':100, 'tags':{}}, 'ua')
    seen = []
    def cb(sid, point):
        seen.append((sid, point))
    tsdb.stream_data('s1', cb)
    assert len(seen) == 1
    assert seen[0][0] == 's1' and seen[0][1]['value']==100

def test_import_csv():
    csv_content = "device,time,val,tag1\ns1,2021-01-01T00:00:00,1.1,x"
    f = io.StringIO(csv_content)
    mapping = {'device':'series_id','time':'timestamp','val':'value','tag1':'t1'}
    tsdb.import_csv(f, mapping)
    assert 's1' in tsdb.series_data
    point = tsdb.series_data['s1'][0]
    assert point['value'] == 1.1
    assert point['tags'] == {'t1':'x'}

def test_compress_series_in_memory():
    t = datetime.datetime(2021,1,1)
    tsdb.record_version('s1', t, {'value':1, 'tags':{}}, 'ua')
    tsdb.record_version('s1', t+datetime.timedelta(seconds=1), {'value':3, 'tags':{}}, 'ua')
    tsdb.record_version('s1', t+datetime.timedelta(seconds=2), {'value':6, 'tags':{}}, 'ua')
    deltas = tsdb.compress_series_in_memory('s1','delta')
    assert deltas == [2,3]
    rle = tsdb.compress_series_in_memory('s1','rle')
    assert rle == [(1,1),(3,1),(6,1)]
    with pytest.raises(ValueError):
        tsdb.compress_series_in_memory('s1','bad')

def test_cache_query():
    calls = {'n':0}
    @tsdb.cache_query('sig1', 100)
    def f(x):
        calls['n'] += 1
        return x*2
    r1 = f(2)
    r2 = f(3)
    assert r1 == 4 and r2 == 4
    assert calls['n'] == 1
    time.sleep(0.15)
    r3 = f(5)
    assert r3 == 10
    assert calls['n'] == 2

def test_enforce_cardinality_limit_function():
    tsdb.enforce_cardinality_limit('s2', 2)
    assert tsdb.cardinality_limits['s2'] == 2
    assert tsdb.series_tag_keys['s2'] == set()
