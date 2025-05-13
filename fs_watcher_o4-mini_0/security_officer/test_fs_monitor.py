import os
import time
import tempfile
import threading
import pytest
from fs_monitor import FileIntegrityMonitor

def test_initial_baseline(tmp_path):
    d = tmp_path / "test"
    d.mkdir()
    fm = FileIntegrityMonitor(str(d))
    res = fm.scan_once()
    assert res['added'] == set()
    assert res['deleted'] == set()
    assert res['modified'] == set()
    assert res['moved'] == set()
    assert "No changes detected" in res['summary']

def test_detect_add_and_delete(tmp_path):
    d = tmp_path / "test2"
    d.mkdir()
    fm = FileIntegrityMonitor(str(d))
    fm.scan_once()
    f1 = d / "a.txt"
    f1.write_text("hello")
    res1 = fm.scan_once()
    assert f1.as_posix() in res1['added']
    assert "1 files added" in res1['summary']
    res2 = fm.scan_once()
    assert f1.as_posix() in res2['deleted'] or res2['deleted'] == set()
    # If file unchanged, it may not show up; remove explicitly
    f1.unlink()
    res3 = fm.scan_once()
    assert f1.as_posix() in res3['deleted']

def test_modify(tmp_path):
    d = tmp_path / "test3"
    d.mkdir()
    f1 = d / "b.txt"
    f1.write_text("one")
    fm = FileIntegrityMonitor(str(d))
    fm.scan_once()
    f1.write_text("two")
    res = fm.scan_once()
    assert f1.as_posix() in res['modified']
    assert "1 files modified" in res['summary']

def test_move_detection(tmp_path):
    d = tmp_path / "test4"
    d.mkdir()
    f1 = d / "c.txt"
    f1.write_text("data")
    fm = FileIntegrityMonitor(str(d))
    fm.enable_move_detection(True)
    fm.scan_once()
    f1.unlink()
    f2 = d / "c2.txt"
    f2.write_text("data")
    res = fm.scan_once()
    assert ('move', (f1.as_posix(), f2.as_posix())) not in []  # sanity
    assert len(res['moved']) == 1
    assert "1 files moved" in res['summary']

def test_ignore_rules(tmp_path):
    d = tmp_path / "test5"
    d.mkdir()
    f1 = d / "temp.swp"
    f1.write_text("tmp")
    fm = FileIntegrityMonitor(str(d))
    fm.add_ignore_rule("*.swp")
    res = fm.scan_once()
    assert res['added'] == set()
    assert "No changes detected" in res['summary']

def test_filters_and_sinks(tmp_path):
    d = tmp_path / "test6"
    d.mkdir()
    f1 = d / "safe.patch"
    f1.write_text("patch")
    events = []
    def filter_patch(path):
        return path.endswith(".patch")
    def sink(evt, info):
        events.append((evt, info))
    fm = FileIntegrityMonitor(str(d))
    fm.register_plugin(filter=filter_patch, sink=sink)
    res = fm.scan_once()
    # patch filtered out, no events
    assert events == []
    # add a normal file
    f2 = d / "normal.txt"
    f2.write_text("hi")
    res2 = fm.scan_once()
    assert any(e[0]=="add" and e[1]==f2.as_posix() for e in events)

def test_thread_pool_and_timeout(tmp_path):
    d = tmp_path / "test7"
    d.mkdir()
    fm = FileIntegrityMonitor(str(d))
    # transform that sleeps to force timeout
    def slow_transform(data):
        time.sleep(0.1)
        return data
    fm.register_plugin(transform=slow_transform)
    fm.set_thread_pool_size(2)
    fm.set_handler_timeout(0.01)
    f1 = d / "x.txt"
    f1.write_bytes(b"hello")
    res = fm.scan_once()
    # hashing timed out; no adds because file not hashed
    assert f1.as_posix() not in res['added']

def test_throttle_rate(tmp_path):
    d = tmp_path / "test8"
    d.mkdir()
    fm = FileIntegrityMonitor(str(d))
    fm.set_throttle_rate(1)
    events = []
    def sink(evt, info):
        events.append((evt, info))
    fm.register_plugin(sink=sink)
    # create two files before scan
    f1 = d / "a.txt"; f1.write_text("1")
    f2 = d / "b.txt"; f2.write_text("2")
    res = fm.scan_once()
    # only one event due to throttle_rate
    assert len(events) == 1
    assert res['metrics']['anomaly_count'] == 1

def test_metrics_endpoint(tmp_path):
    d = tmp_path / "test9"
    d.mkdir()
    fm = FileIntegrityMonitor(str(d))
    recorded = []
    def cb(metrics):
        recorded.append(metrics)
    fm.start_metrics_endpoint(cb)
    f1 = d / "a.txt"; f1.write_text("1")
    fm.scan_once()
    assert recorded
    assert 'latency' in recorded[0]
    assert 'anomaly_count' in recorded[0]

def test_generate_change_summary():
    fm = FileIntegrityMonitor(".")
    s = fm.generate_change_summary(2,1,3,4)
    assert "2 files added" in s
    assert "1 files deleted" in s
    assert "3 files modified" in s
    assert "4 files moved" in s

def test_configure_logging():
    fm = FileIntegrityMonitor(".")
    fm.configure_logging(logging.WARNING)
    assert fm.logger.level == logging.WARNING
