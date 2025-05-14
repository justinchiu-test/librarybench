import os
import tempfile
import datetime
import pickle
import matplotlib
from tsdb.tsdb import TimeSeriesDB

def test_import_csv_and_query(tmp_path):
    csv_file = tmp_path / "data.csv"
    content = "time,host,region,cpu,mem\n"
    content += "2021-01-01T00:00:00,web-01,us-east,10,512\n"
    content += "2021-01-01T01:00:00,web-02,us-west,20,1024\n"
    csv_file.write_text(content)
    db = TimeSeriesDB()
    db.import_csv(str(csv_file), "time", ["host", "region"], ["cpu", "mem"])
    all_data = db.query()
    assert len(all_data) == 2
    ts0, metrics0 = all_data[0]
    assert metrics0["cpu"] == 10
    assert metrics0["mem"] == 512
    filtered = db.query(metric="cpu", filters={"host": "web-02"})
    assert len(filtered) == 1
    assert filtered[0][1] == 20

def test_handle_missing_data_zero_and_carry_and_drop():
    t0 = datetime.datetime(2021,1,1,0,0)
    series = [(t0, 1), (t0+datetime.timedelta(hours=2), 3)]
    db = TimeSeriesDB()
    zeroed = db.handle_missing_data(series, method='zero', freq=datetime.timedelta(hours=1))
    assert len(zeroed) == 3
    assert zeroed[1][1] == 0
    carried = db.handle_missing_data(series, method='carry', freq=datetime.timedelta(hours=1))
    assert carried[1][1] == 1
    dropped = db.handle_missing_data(series, method='drop', freq=datetime.timedelta(hours=1))
    assert len(dropped) == 2

def test_generate_rollups_and_query_interval():
    db = TimeSeriesDB()
    base = datetime.datetime(2021,1,1,10,15)
    db.ingest(base, {"host":"a"}, {"cpu":10})
    db.ingest(base+datetime.timedelta(minutes=30), {"host":"a"}, {"cpu":30})
    db.generate_rollups()
    hourly = db.query(metric="cpu", filters={"host":"a"}, interval='hour')
    assert len(hourly) == 1
    assert hourly[0][1] == 20

def test_query_by_tags():
    db = TimeSeriesDB()
    ts = datetime.datetime.now()
    db.ingest(ts, {"host":"x","region":"y"}, {"cpu":5})
    res = db.query_by_tags({"host":"x"})
    assert len(res) == 1
    assert res[0][1]["cpu"] == 5

def test_interpolate_step_and_linear():
    t0 = datetime.datetime(2021,1,1,0,0)
    series = [(t0, 0), (t0+datetime.timedelta(hours=2), 20)]
    db = TimeSeriesDB()
    step = db.interpolate(series, method='step')
    assert len(step) == 3
    assert step[1][1] == 0
    linear = db.interpolate(series, method='linear')
    assert linear[1][1] == 10

def test_snapshot_and_load(tmp_path):
    db = TimeSeriesDB()
    ts = datetime.datetime.now()
    db.ingest(ts, {"h":"1"}, {"cpu":7})
    snap = tmp_path / "snap.pkl"
    db.snapshot(str(snap))
    newdb = TimeSeriesDB()
    newdb.load_snapshot(str(snap))
    data = newdb.query()
    assert len(data) == 1
    assert data[0][1]["cpu"] == 7

def test_compress_and_decompress():
    db = TimeSeriesDB()
    t0 = datetime.datetime(2021,1,1)
    db.ingest(t0, {}, {"v": 100})
    db.ingest(t0+datetime.timedelta(seconds=1), {}, {"v": 110})
    orig = list(db.store)
    db.compress_memory()
    assert db._compressed is not None
    db.decompress_memory()
    assert db._compressed is None
    assert db.store == orig

def test_plot_series_returns_figure():
    db = TimeSeriesDB()
    series = [(datetime.datetime(2021,1,1), 1), (datetime.datetime(2021,1,1,1), 2)]
    fig = db.plot_series(series)
    from matplotlib.figure import Figure
    assert isinstance(fig, Figure)
    plt_close = matplotlib.pyplot.close
    plt_close(fig)

def test_export_json_and_ndjson():
    db = TimeSeriesDB()
    series = [(datetime.datetime(2021,1,1), 5), (datetime.datetime(2021,1,1,1), 10)]
    j = db.export_json(series)
    obj = json.loads(j)
    assert isinstance(obj, list) and obj[0]["value"] == 5
    nd = db.export_json(series, ndjson=True)
    lines = nd.split('\n')
    assert json.loads(lines[1])["value"] == 10
