import os
import csv
import datetime
import tempfile
import time
import pytest
from zoneinfo import ZoneInfo

import timeseries_module as tm

def test_export_csv():
    s1 = {'id': 's1', 'tags': {'env': 'prod'}, 'data': [
        (datetime.datetime(2021,1,1,12,0, tzinfo=datetime.timezone.utc), 10),
        (datetime.datetime(2021,1,1,13,0, tzinfo=datetime.timezone.utc), 20),
    ]}
    s2 = {'id': 's2', 'tags': {'env': 'dev'}, 'data': [
        (datetime.datetime(2021,1,1,12,30, tzinfo=datetime.timezone.utc), 5),
    ]}
    start = datetime.datetime(2021,1,1,11,0, tzinfo=datetime.timezone.utc)
    end = datetime.datetime(2021,1,1,12,30, tzinfo=datetime.timezone.utc)
    csv_str = tm.export_csv([s1, s2], start, end, {'env': 'prod'})
    lines = csv_str.strip().splitlines()
    assert lines[0] == 'timestamp,series_id,value'
    assert '2021-01-01T12:00:00+00:00,s1,10' in lines

def test_define_alert():
    alert = tm.define_alert('high_err', 'e1', 'value>5', 'critical', ['email'])
    assert alert['name'] == 'high_err'
    assert tm._alerts['high_err']['condition'] == 'value>5'

def test_convert_timezone():
    utc = datetime.timezone.utc
    start = datetime.datetime(2021,3,14,6,0, tzinfo=utc)
    end = datetime.datetime(2021,3,14,7,0, tzinfo=utc)
    res = tm.convert_timezone({'start_time': start, 'end_time': end}, 'America/New_York')
    # DST starts on 2021-03-14 at 2am local, so 6 UTC is 2am EST (-5), 7 UTC is 3am EDT (-4)
    assert res['start_time'].tzinfo == ZoneInfo('America/New_York')
    assert res['end_time'].utcoffset() == datetime.timedelta(hours=-4)

def test_join_series_inner():
    t1 = datetime.datetime(2021,1,1,0,0)
    # corrected to include a zero-second before specifying microseconds
    t2 = datetime.datetime(2021,1,1,0,0,0,500000)  # 0.5s later
    a = [(t1, 1)]
    b = [(t2, 2)]
    joined = tm.join_series(a, b, 'inner', 1000)
    assert len(joined) == 1
    assert joined[0]['a'] == 1 and joined[0]['b'] == 2

def test_join_series_outer():
    t1 = datetime.datetime(2021,1,1,0,0)
    t2 = datetime.datetime(2021,1,1,0,2)
    a = [(t1, 1)]
    b = [(t2, 2)]
    joined = tm.join_series(a, b, 'outer', 1000)
    assert len(joined) == 2
    # first row has a, no b
    assert joined[0]['a'] == 1 and joined[0]['b'] is None
    # second has b, no a
    assert joined[1]['b'] == 2 and joined[1]['a'] is None

def test_stream_updates():
    received = []
    def cb(sid, dp):
        received.append((sid, dp))
    sub = tm.stream_updates(['s1'], cb)
    tm.publish_update('s1', {'val': 100})
    assert received == [('s1', {'val': 100})]
    sub.unsubscribe()
    tm.publish_update('s1', {'val': 200})
    assert received == [('s1', {'val': 100})]

def test_import_csv(tmp_path):
    file = tmp_path / "data.csv"
    data = [
        {'a': '1', 'b': '2.5', 'c': 'hello'},
        {'a': '3', 'b': '4.0', 'c': 'world'},
    ]
    with open(file, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['a','b','c'])
        w.writeheader()
        w.writerows(data)
    schema = {'a': int, 'b': float, 'c': str}
    res = tm.import_csv(str(file), schema)
    assert res[0]['a'] == 1 and isinstance(res[0]['b'], float)
    assert res[1]['c'] == 'world'

def test_record_write_history():
    before = len(tm._write_history)
    entry = tm.record_write_history('s1', 'updated', 'user@example.com')
    after = len(tm._write_history)
    assert after == before + 1
    assert entry in tm._write_history

def test_apply_compression():
    assert tm.apply_compression('s1', 'gzip')
    assert tm._compression_registry['s1'] == 'gzip'

def test_cache_query_results():
    assert tm.cache_query_results('q1', 60)
    entry = tm._cache_registry.get('q1')
    assert entry and entry['duration'] == 60

def test_limit_cardinality_and_add_tag_value():
    tm.limit_cardinality('s1', 'region', 2)
    # Add up to limit
    assert tm.add_tag_value('s1', 'region', 'us')
    assert tm.add_tag_value('s1', 'region', 'eu')
    # Exceed
    with pytest.raises(ValueError):
        tm.add_tag_value('s1', 'region', 'apac')
