import os
import tempfile
import pandas as pd
import pytest
import gzip
import pickle
import zlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import time_series_engine as tse

def setup_function():
    # clear global stores before each test
    tse.series_quotes.clear()
    tse.series_trades.clear()
    tse.alerts.clear()
    tse.audit_log.clear()
    tse.compressed_series.clear()
    tse.cache_store.clear()
    tse.subscribers.clear()
    tse.cardinality_limits.clear()
    tse.cardinality_values.clear()

def test_import_csv(tmp_path):
    data = "ts,price,vol\n2021-01-01T00:00:00Z,100,5\n"
    f = tmp_path / "hist.csv"
    f.write_text(data)
    df = tse.import_csv(str(f), {'ts': 'timestamp', 'price': 'price', 'vol': 'volume'})
    assert 'timestamp' in df.columns
    assert df.iloc[0]['price'] == 100

def test_export_csv():
    # prepare quotes
    dfq = pd.DataFrame({
        'timestamp': [datetime(2021,1,1,0,0,0), datetime(2021,1,1,0,0,1)],
        'bid': [99, 100],
        'ask': [101, 102]
    })
    dftr = pd.DataFrame({
        'timestamp': [datetime(2021,1,1,0,0,0)],
        'price': [100],
        'volume': [10]
    })
    tse.series_quotes['s1'] = dfq
    tse.series_trades['s1'] = dftr
    csv = tse.export_csv(['s1'], datetime(2021,1,1,0,0,0), datetime(2021,1,1,0,0,1),
                         ['series_id','timestamp','bid','ask','price','volume'])
    # CSV header and lines
    lines = csv.strip().splitlines()
    assert 'series_id' in lines[0]
    assert len(lines) == 4  # 3 rows + header

def test_define_alert():
    tse.define_alert('a1', 's1', '>', 100, 'target1')
    assert 'a1' in tse.alerts
    cfg = tse.alerts['a1']
    assert cfg['operator'] == '>'

def test_convert_timezone():
    df = pd.DataFrame({
        'timestamp': ['2021-01-01T12:00:00', '2021-06-01T12:00:00'],
        'price': [1,2]
    })
    out = tse.convert_timezone(df, 'America/New_York')
    tz = out['timestamp'].dt.tz
    assert str(tz) == 'America/New_York'

def test_join_series():
    base = pd.DataFrame({
        'timestamp': [datetime(2021,1,1,0,0,0), datetime(2021,1,1,0,0,2)],
        'bid': [1,2]
    })
    ovr = pd.DataFrame({
        'timestamp': [datetime(2021,1,1,0,0,1)],
        'price': [1.5]
    })
    res = tse.join_series(base, ovr, 'left', '1s')
    assert 'price' in res.columns
    assert res.iloc[0]['price'] == pytest.approx(1.5, rel=1e-3)

    res2 = tse.join_series(base, ovr, 'inner', '1s')
    assert len(res2) == 1

def test_stream_updates():
    gen = tse.stream_updates('s1')
    # put an update
    q = tse.subscribers['s1'][0]
    q.put({'price': 100})
    v = next(gen)
    assert v == {'price': 100}

def test_record_audit():
    tse.record_audit('s1', 'op1', 'user1', datetime.utcnow())
    assert tse.audit_log[-1]['operation'] == 'op1'

def test_apply_compression():
    df = pd.DataFrame({'timestamp': [1,2,3], 'bid': [1,2,3]})
    tse.series_quotes['s1'] = df
    tse.apply_compression('s1', 'gzip')
    comp = tse.compressed_series['s1']
    data = gzip.decompress(comp)
    df2 = pickle.loads(data)
    pd.testing.assert_frame_equal(df, df2)

    tse.apply_compression('s1', 'zlib')
    comp2 = tse.compressed_series['s1']
    data2 = zlib.decompress(comp2)
    df3 = pickle.loads(data2)
    pd.testing.assert_frame_equal(df, df3)

    with pytest.raises(ValueError):
        tse.apply_compression('s1', 'unknown')

def test_cache_query():
    tse.cache_query('q1', 5)
    assert 'q1' in tse.cache_store
    exp = tse.cache_store['q1']['expire']
    assert exp > datetime.utcnow()

def test_limit_cardinality_and_add():
    tse.limit_cardinality('s1', 'tagA', 2)
    # add two values
    tse.add_tag_to_series('s1', 'tagA', 'v1')
    tse.add_tag_to_series('s1', 'tagA', 'v2')
    # third should fail
    with pytest.raises(ValueError):
        tse.add_tag_to_series('s1', 'tagA', 'v3')
    # adding existing should be fine
    tse.add_tag_to_series('s1', 'tagA', 'v2')
