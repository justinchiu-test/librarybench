import os
import csv
import time
import pytest
from datetime import datetime, timedelta, timezone
from timeseries import TimeSeriesDB

def test_record_write_and_history():
    db = TimeSeriesDB()
    db.record_write("s1", datetime(2021,1,1, tzinfo=timezone.utc), 10, {"k":"v"}, "user1")
    db.record_write("s1", datetime(2021,1,2, tzinfo=timezone.utc), 20, {"k":"v2"}, "user2")
    assert len(db.series["s1"]) == 2
    assert len(db.history) == 2
    sid, ts, val, tags, uid = db.history[1]
    assert sid == "s1" and val == 20 and uid == "user2"
    assert tags == {"k":"v2"}

def test_export_csv_and_filter():
    db = TimeSeriesDB()
    t1 = datetime(2021,1,1,12,0, tzinfo=timezone.utc)
    t2 = datetime(2021,1,2,12,0, tzinfo=timezone.utc)
    db.record_write("s1", t1, 1, {"a":"x"}, "u")
    db.record_write("s2", t2, 2, {"a":"y"}, "u")
    csv_out = db.export_csv(["s1","s2"], t1, t2, {"a":"x"})
    lines = csv_out.strip().splitlines()
    assert lines[0].split(",")[:3] == ["series_id","timestamp","a"]
    assert len(lines) == 2
    assert "s1" in lines[1]

def test_define_alert_triggers():
    db = TimeSeriesDB()
    calls = []
    def cb(rule_id, sid, rec):
        calls.append((rule_id, sid, rec["value"]))
    db.define_alert("r1", "s1", 5, ">", cb)
    db.record_write("s1", datetime.now(timezone.utc), 10, {}, "u")
    assert calls == [("r1","s1",10)]

def test_convert_timezone():
    db = TimeSeriesDB()
    q = {"start": datetime(2021,1,1,0,0), "end": datetime(2021,1,1,12,0)}
    out = db.convert_timezone(q, "America/New_York")
    assert out["start"].tzinfo.key == "America/New_York"
    # Check offset approx -5 or -4 depending on DST
    # For Jan it is -5
    assert out["start"].utcoffset().total_seconds() == -5*3600

def test_join_series_types():
    db = TimeSeriesDB()
    t1 = datetime(2021,1,1, tzinfo=timezone.utc)
    t2 = datetime(2021,1,2, tzinfo=timezone.utc)
    db.record_write("p", t1, 1, {}, "u")
    db.record_write("p", t2, 2, {}, "u")
    db.record_write("o", t2, 20, {}, "u")
    inner = db.join_series("p", ["o"], "inner")
    assert len(inner)==1 and inner[0]["timestamp"]==t2
    left = db.join_series("p", ["o"], "left")
    assert len(left)==2
    outer = db.join_series("p", ["o"], "outer")
    assert len(outer)==2

def test_stream_updates():
    db = TimeSeriesDB()
    q = db.stream_updates("s1")
    t = datetime.now(timezone.utc)
    db.record_write("s1", t, 5, {}, "u")
    upd = q.get(timeout=1)
    assert upd["value"] == 5 and upd["timestamp"] == t

def test_import_csv(tmp_path):
    # create csv
    path = tmp_path/"data.csv"
    with open(path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["time","val","tg"])
        writer.writerow(["2021-01-01T00:00:00", "3.5", "tag1"])
    db = TimeSeriesDB()
    cfg = {"fixed_series_id":"simp","timestamp":"time","value":"val","tags":{"t":"tg"}}
    db.import_csv(str(path), cfg)
    assert "simp" in db.series
    rec = db.series["simp"][0]
    assert rec["value"] == 3.5 and rec["tags"]["t"] == "tag1"

def test_apply_compression():
    db = TimeSeriesDB()
    db.apply_compression("s1", "delta", 100)
    assert db.compression["s1"]["method"] == "delta"
    assert db.compression["s1"]["block_size"] == 100

def test_cache_query_decorator(monkeypatch):
    db = TimeSeriesDB()
    calls = {"count":0}
    @db.cache_query("sig", ttl=1)
    def compute(x):
        calls["count"] += 1
        return x*2
    res1 = compute(2)
    res2 = compute(2)
    assert res1 == 4 and res2 == 4
    assert calls["count"] == 1
    # expire cache
    monkeypatch.setattr(time, "time", lambda: time.time()+2)
    res3 = compute(3)
    assert calls["count"] == 2 and res3 == 6

def test_limit_cardinality():
    db = TimeSeriesDB()
    db.limit_cardinality("s1", "k", 2)
    db.record_write("s1", datetime(2021,1,1, tzinfo=timezone.utc), 1, {"k":"v1"}, "u")
    db.record_write("s1", datetime(2021,1,2, tzinfo=timezone.utc), 2, {"k":"v2"}, "u")
    with pytest.raises(Exception):
        db.record_write("s1", datetime(2021,1,3, tzinfo=timezone.utc), 3, {"k":"v3"}, "u")
