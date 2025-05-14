import pytest
import pandas as pd
import numpy as np
import tempfile
import json
from timeseries_toolkit import TimeSeriesToolkit

def create_sample_csv(tmp_path):
    csv_path = tmp_path / "sample.csv"
    df = pd.DataFrame({
        'timestamp': ['2021-01-01 00:00','2021-01-01 01:00','2021-01-01 02:00','2021-01-02 00:00'],
        'device_id': ['d1','d1','d2','d1'],
        'location': ['loc1','loc1','loc2','loc1'],
        'measurement': [1, np.nan, 3, 5]
    })
    df.to_csv(csv_path, index=False)
    return str(csv_path), df

def test_import_and_handle_missing(tmp_path):
    path, orig_df = create_sample_csv(tmp_path)
    tt = TimeSeriesToolkit()
    df = tt.import_csv(path)
    assert 'measurement' in df.columns
    # zero fill
    df_zero = tt.handle_missing_data(strategy='zero')
    assert df_zero.loc[pd.to_datetime('2021-01-01 01:00'),'measurement'] == 0
    # reload for next test
    tt.import_csv(path)
    df_carry = tt.handle_missing_data(strategy='carry_forward')
    assert df_carry.loc[pd.to_datetime('2021-01-01 01:00'),'measurement'] == 1
    # reload
    tt.import_csv(path)
    df_drop = tt.handle_missing_data(strategy='drop')
    assert df_drop['measurement'].isna().sum() == 0
    assert len(df_drop) == 3

def test_generate_rollups():
    tt = TimeSeriesToolkit()
    idx = pd.date_range('2021-01-01', periods=24, freq='H')
    df = pd.DataFrame({'measurement': np.arange(24)}, index=idx)
    tt.data = df
    rollups = tt.generate_rollups()
    assert 'hourly' in rollups and 'daily' in rollups
    assert len(rollups['hourly']) == 24
    assert len(rollups['daily']) == 2

def test_query_and_query_by_tags(tmp_path):
    path, orig_df = create_sample_csv(tmp_path)
    tt = TimeSeriesToolkit()
    tt.import_csv(path)
    tt.handle_missing_data('zero')
    q = tt.query('measurement > 2')
    assert all(q['measurement'] > 2)
    qb = tt.query_by_tags(device_id='d1', location='loc1',
                          start='2021-01-01', end='2021-01-01 23:59')
    assert all(qb['device_id']=='d1')
    assert all(qb['location']=='loc1')
    assert qb.index.min() >= pd.to_datetime('2021-01-01')

def test_interpolate():
    tt = TimeSeriesToolkit()
    idx = pd.date_range('2021-01-01', periods=5, freq='D')
    df = pd.DataFrame({'x':[0,np.nan, np.nan,4,5]}, index=idx)
    tt.data = df.copy()
    df_lin = tt.interpolate(method='linear')
    assert pytest.approx(df_lin.iloc[1,0]) == (0 + (4-0)/3*1)
    tt.data = df.copy()
    df_step = tt.interpolate(method='step')
    assert df_step.iloc[1,0] == 0
    tt.data = df.copy()
    df_spl = tt.interpolate(method='spline')
    assert not df_spl.isnull().values.any()

def test_snapshot():
    tt = TimeSeriesToolkit()
    tt.data = pd.DataFrame({'a':[1,2,3]})
    tt.snapshot('snap1')
    assert 'snap1' in tt.snapshots
    assert tt.snapshots['snap1'].equals(tt.data)

def test_compress_decompress():
    tt = TimeSeriesToolkit()
    idx = pd.date_range('2021-01-01', periods=4, freq='H')
    df = pd.DataFrame({
        'num':[1,2,2,5],
        'label':['a','b','b','c']
    }, index=idx)
    tt.data = df
    comp = tt.compress_memory()
    assert 'numeric' in comp and 'non_numeric' in comp and 'index' in comp
    df2 = tt.decompress_memory()
    pd.testing.assert_frame_equal(df2, df)

def test_plot_series():
    tt = TimeSeriesToolkit()
    idx = pd.date_range('2021-01-01', periods=3, freq='H')
    tt.data = pd.DataFrame({'val':[1,2,3]}, index=idx)
    tt.generate_rollups()
    fig = tt.plot_series()
    import matplotlib.figure
    assert isinstance(fig, matplotlib.figure.Figure)

def test_export_json():
    tt = TimeSeriesToolkit()
    idx = pd.date_range('2021-01-01', periods=2, freq='H')
    tt.data = pd.DataFrame({'val':[10,20]}, index=idx)
    js = tt.export_json()
    data = json.loads(js)
    assert isinstance(data, list)
    assert data[0]['val'] == 10
