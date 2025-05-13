import os
import tempfile
import pickle
import json
import numpy as np
import pandas as pd
import pytest
import matplotlib
matplotlib.use('Agg')
from climate_engine import ClimateEngine

def create_csv(tmp_path, rows):
    fp = tmp_path / "data.csv"
    df = pd.DataFrame(rows)
    df.to_csv(str(fp), index=False)
    return str(fp)

def test_import_and_basic_df(tmp_path):
    rows = [
        {'station_id': 'A', 'region': 'North', 'timestamp': '2020-01-01', 'temperature': 10},
        {'station_id': 'B', 'region': 'South', 'timestamp': '2020-01-02', 'temperature': 20},
    ]
    fp = create_csv(tmp_path, rows)
    eng = ClimateEngine()
    df = eng.import_csv(fp)
    assert 'A' in df['station_id'].values
    assert 'B' in df['station_id'].values
    assert df.loc[pd.Timestamp('2020-01-01'), 'temperature'] == 10

def test_handle_missing_data_strategies():
    eng = ClimateEngine()
    eng.df = pd.DataFrame({
        'station_id': ['A','A','A'],
        'region': ['X','X','X'],
        'temperature': [np.nan, 5, np.nan],
    }, index=pd.to_datetime(['2020-01-01', '2020-01-02', '2020-01-03']))
    df_zero = eng.handle_missing_data('zero')
    assert (df_zero['temperature'] == [0,5,0]).all()
    eng.df = df_zero.copy()
    df_ff = eng.handle_missing_data('forward')
    assert (df_ff['temperature'] == [0,5,5]).all()
    eng.df = pd.DataFrame({
        'station_id': ['A','A','A'],
        'region': ['X','X','X'],
        'temperature': [1, np.nan, 3],
    }, index=pd.to_datetime(['2020-01-01', '2020-01-02', '2020-01-03']))
    df_drop = eng.handle_missing_data('drop')
    assert len(df_drop) == 2

def test_generate_rollups():
    eng = ClimateEngine()
    dates = pd.date_range('2020-01-01', periods=3, freq='D')
    eng.df = pd.DataFrame({
        'station_id': ['A','A','A'],
        'region': ['X','X','X'],
        'temperature': [1,2,3],
    }, index=dates)
    rolls = eng.generate_rollups()
    assert 'daily' in rolls and 'monthly' in rolls and 'annual' in rolls
    assert rolls['daily'].loc['2020-01-02','temperature'] == 2

def test_query_and_by_tags():
    eng = ClimateEngine()
    dates = pd.date_range('2020-01-01', periods=2, freq='D')
    eng.df = pd.DataFrame({
        'station_id': ['A','B'],
        'region': ['X','Y'],
        'temperature': [1,2],
    }, index=dates)
    res = eng.query({'region':'X'})
    assert res.shape[0] == 1 and res.iloc[0]['station_id']=='A'
    res2 = eng.query(agg={'temperature':'sum'})
    assert res2['temperature'] == 3
    res3 = eng.query_by_tags({'station_id':'B'})
    assert res3.iloc[0]['region']=='Y'

def test_interpolate_methods():
    eng = ClimateEngine()
    dates = pd.date_range('2020-01-01', periods=5, freq='D')
    temps = [1, np.nan, np.nan, 4, 5]
    eng.df = pd.DataFrame({
        'station_id': ['A']*5,
        'region': ['X']*5,
        'temperature': temps,
    }, index=dates)
    lin = eng.interpolate('linear')
    assert pytest.approx(lin.loc['2020-01-03','temperature']) == 2.3333333
    eng.df['temperature'] = temps
    stp = eng.interpolate('step')
    assert stp.loc['2020-01-03','temperature'] == 1
    eng.df['temperature'] = temps
    spl = eng.interpolate('spline')
    assert not spl['temperature'].isna().any()

def test_snapshot_and_load(tmp_path):
    eng = ClimateEngine()
    eng.df = pd.DataFrame({
        'station_id':['A'],
        'region':['X'],
        'temperature':[10],
    }, index=pd.to_datetime(['2020-01-01']))
    fp = tmp_path / "snap.pkl"
    eng.snapshot(str(fp))
    with open(str(fp),'rb') as f:
        loaded = pickle.load(f)
    assert isinstance(loaded, ClimateEngine)
    assert loaded.df.iloc[0]['temperature'] == 10

def test_compress_memory():
    eng = ClimateEngine()
    dates = pd.date_range('2020-01-01', periods=3, freq='D')
    eng.df = pd.DataFrame({
        'station_id':['A']*3,
        'region':['X']*3,
        'temperature':[10,12,15],
        'precip':[0,1,1],
    }, index=dates)
    comp = eng.compress_memory()
    assert comp.loc['2020-01-02','temperature'] == 2
    assert comp.loc['2020-01-03','precip'] == 0

def test_plot_series():
    eng = ClimateEngine()
    dates = pd.date_range('2020-01-01', periods=3)
    eng.df = pd.DataFrame({
        'station_id':['A']*3,
        'region':['X']*3,
        'temperature':[1,2,3],
    }, index=dates)
    fig = eng.plot_series('A','temperature')
    assert hasattr(fig, 'axes')
    assert len(fig.axes[0].lines) == 1

def test_export_json():
    eng = ClimateEngine()
    dates = pd.date_range('2020-01-01', periods=2)
    eng.df = pd.DataFrame({
        'station_id':['A','B'],
        'region':['X','Y'],
        'temperature':[5,6],
    }, index=dates)
    j = eng.export_json()
    recs = json.loads(j)
    assert isinstance(recs, list) and len(recs) == 2
    j2 = eng.export_json(newline_delimited=True)
    lines = j2.split('\n')
    assert len(lines) == 2
