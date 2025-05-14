import os
import csv
import time
import pytest
from datetime import datetime, timezone
from tsdb import (
    import_csv, export_csv, define_alert, convert_timezone,
    join_series, stream_updates, record_version,
    apply_compression, cache_query, limit_cardinality,
    _series_data, _audit_trail, _cache, _cardinality
)

def test_import_and_export_csv(tmp_path):
    # Prepare CSV file
    csv_file = tmp_path / "data.csv"
    rows = [
        {'id': 'exp1', 'time': '2023-01-01T00:00:00', 'value': '10'},
        {'id': 'exp1', 'time': '2023-01-02T00:00:00', 'value': '20'},
        {'id': 'exp2', 'time': '2023-01-01T00:00:00', 'value': '5'}
    ]
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id','time','value'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    mapping = {'id':'experiment_id','time':'time','value':'value'}
    assert import_csv(str(csv_file), mapping)
    # Export for exp1 between dates
    start = datetime(2023,1,1,0,0,0)
    end = datetime(2023,1,1,23,59,59)
    out = export_csv(['exp1'], (start, end), include_metadata=False)
    reader = csv.DictReader(out.splitlines())
    data = list(reader)
    assert len(data) == 1
    assert data[0]['experiment_id'] == 'exp1'
    assert data[0]['value'] == '10'

def test_define_alert():
    series = [
        {'time': datetime.now(), 'value': 1},
        {'time': datetime.now(), 'value': 100},
    ]
    recips = ['a@x.com']
    # greater than threshold
    alert = define_alert(series, '>', 50, recips)
    assert alert == recips
    # no alert
    alert2 = define_alert(series, '<', 0, recips)
    assert alert2 == []

def test_convert_timezone():
    q = [{'time': datetime(2023,1,1,12,0,0, tzinfo=timezone.utc)}]
    conv = convert_timezone(q, 'UTC')
    assert conv[0]['time'].tzinfo.key == 'UTC'
    # convert to US/Eastern
    conv2 = convert_timezone(q, 'US/Eastern')
    assert conv2[0]['time'].tzinfo.key in ('US/Eastern','America/New_York')

def test_join_series():
    t1 = datetime(2023,1,1,0,0,0)
    t2 = datetime(2023,1,2,0,0,0)
    expr = [{'time':t1,'value':5},{'time':t2,'value':10}]
    pheno = [{'time':t1,'value':2}]
    inner = join_series(expr, pheno, 'inner')
    assert len(inner) == 1
    assert inner[0]['expression'] == 5
    outer = join_series(expr, pheno, 'outer')
    assert len(outer) == 2
    # check missing fields
    assert any(e['phenotype'] is None for e in outer)

def test_stream_updates():
    data = [1,2,3]
    assert list(stream_updates(data)) == [1,2,3]

def test_record_version():
    _audit_trail.clear()
    assert record_version({'a':1}, 'user1', 'reason1')
    assert len(_audit_trail) == 1
    rec = _audit_trail[0]
    assert rec['user_id'] == 'user1'
    assert rec['change_reason'] == 'reason1'
    assert 'timestamp' in rec

def test_apply_compression():
    out = apply_compression('s1','gzip')
    assert out == b's1:gzip'
    with pytest.raises(ValueError):
        apply_compression('s1','zip')

def test_cache_query():
    calls = {'count': 0}
    @cache_query('sig1', ttl=1)
    def f(x):
        calls['count'] += 1
        return x * 2
    res1 = f(5)
    res2 = f(5)
    assert res1 == 10 and res2 == 10
    assert calls['count'] == 1
    # after TTL expire
    time.sleep(1.1)
    res3 = f(5)
    assert calls['count'] == 2

def test_limit_cardinality():
    _cardinality.clear()
    assert limit_cardinality('series1', 'tagA', 3)
    assert _cardinality['series1']['tagA'] == 3
