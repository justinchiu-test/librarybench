import os
import time
import shutil
import threading
import tempfile
import logging
import json
import urllib.request
import pytest
from filewatcher import FileWatcher

def test_scan_create_modify_delete(tmp_path):
    d = tmp_path / "cfg"
    d.mkdir()
    fw = FileWatcher(paths=[str(d)])
    # create
    f1 = d / "a.txt"
    f1.write_text("hello")
    events = fw.scan_once()
    assert any(e['type']=='created' and e['path']==str(f1) for e in events)
    # modify
    f1.write_text("world")
    events = fw.scan_once()
    assert any(e['type']=='modified' and e['path']==str(f1) for e in events)
    # delete
    f1.unlink()
    events = fw.scan_once()
    assert any(e['type']=='deleted' and e['path']==str(f1) for e in events)

def test_ignore_rules(tmp_path):
    d = tmp_path / "cfg"
    d.mkdir()
    f1 = d / "a.tmp"
    f1.write_text("IGNORE")
    fw = FileWatcher(paths=[str(d)])
    fw.add_ignore_rule("*.tmp")
    events = fw.scan_once()
    assert events == []

def test_move_detection(tmp_path):
    d = tmp_path / "cfg"
    d.mkdir()
    fw = FileWatcher(paths=[str(d)])
    fw.enable_move_detection()
    # initial create
    f1 = d / "one.txt"
    f1.write_text("data")
    fw.scan_once()
    # rename
    f2 = d / "two.txt"
    f1.rename(f2)
    events = fw.scan_once()
    # should detect moved, not separate delete/create
    assert any(e['type']=='moved' and e['src_path']==str(f1) and e['dest_path']==str(f2) for e in events)
    summary = fw.generate_change_summary()
    assert "1 files moved" in summary

def test_register_plugin_and_filter(tmp_path):
    d = tmp_path / "cfg"
    d.mkdir()
    f1 = d / "x.txt"
    called = []
    def flt(e):
        return e['path'].endswith("x.txt")
    def sink(e):
        called.append(e)
    fw = FileWatcher(paths=[str(d)])
    fw.register_plugin(flt, sink)
    f1.write_text("hi")
    ev = fw.scan_once()
    time.sleep(0.1)
    assert len(called)==1
    assert called[0]['type']=='created'

def test_thread_pool_and_timeout_and_throttle(tmp_path):
    d = tmp_path / "cfg"
    d.mkdir()
    f1 = d / "a.txt"
    calls = []
    def sink(e):
        calls.append(e)
    fw = FileWatcher(paths=[str(d)])
    fw.register_plugin(lambda e: True, sink)
    fw.set_thread_pool_size(2)
    assert fw.executor._max_workers == 2
    # test timeout
    def slow_sink(e):
        time.sleep(0.2)
        calls.append('slow')
    fw.register_plugin(lambda e: True, slow_sink)
    fw.set_handler_timeout(0.1)
    # test throttle
    fw.set_throttle_rate(1)
    # create multiple files
    for i in range(3):
        p = d / f"f{i}.txt"
        p.write_text(str(i))
    events = fw.scan_once()
    # allow handlers
    time.sleep(0.5)
    # sink called for all created by first plugin
    assert len([c for c in calls if isinstance(c, dict)]) == 3
    # slow_sink should have timed out, so no 'slow'
    assert 'slow' not in calls
    # throttle: only 1 call per second for slow_sink but none due to timeout

def test_configure_logging():
    fw = FileWatcher()
    fw.configure_logging(logging.DEBUG)
    assert fw.logger.level == logging.DEBUG

def test_metrics_endpoint(tmp_path):
    d = tmp_path / "cfg"
    d.mkdir()
    fw = FileWatcher(paths=[str(d)])
    fw.start_metrics_endpoint(port=0)
    # create a file to generate some metrics
    f1 = d / "a.txt"
    f1.write_text("1")
    fw.scan_once()
    time.sleep(0.1)
    # fetch metrics
    url = f"http://127.0.0.1:{fw.metrics_port}/"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    assert 'events_count' in data
    assert 'avg_latency' in data
    assert 'queue_size' in data
