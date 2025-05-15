import pytest
import time
import logging
import sys
from queue import Queue
import argparse
from unified.compliance_officer.pipeline.compliance import (
    tumbling_window, sliding_window, add_serializer, serializers,
    throttle_upstream, watermark_event_time, halt_on_error,
    skip_error, setup_logging, cli_manage, parallelize_stages,
    track_lineage, lineage_store
)

def test_tumbling_window_empty():
    assert tumbling_window([], 10) == []

def test_tumbling_window_basic():
    tx = [{'timestamp': i} for i in range(5)]
    windows = tumbling_window(tx, 2)
    assert len(windows) == 3
    assert windows[0] == [{'timestamp': 0}, {'timestamp':1}]
    assert windows[-1] == [{'timestamp':4}]

def test_sliding_window_empty():
    assert sliding_window([], 5) == []

def test_sliding_window_basic():
    tx = [{'timestamp': i} for i in range(5)]
    windows = sliding_window(tx, 3, slide=2)
    # windows: [0-3),[2-5),[4-7)
    assert len(windows) == 3
    assert windows[0] == [{'timestamp':0},{'timestamp':1},{'timestamp':2}]
    assert windows[1] == [{'timestamp':2},{'timestamp':3},{'timestamp':4}]

def test_add_serializer():
    def ser(x): return b'data'
    add_serializer('avro', ser)
    assert 'avro' in serializers
    assert serializers['avro'](None) == b'data'

def test_throttle_upstream():
    q = Queue()
    @throttle_upstream(2)
    def process(q):
        return "ok"
    # queue size below threshold
    q.queue.clear()
    result = process(q)
    assert result == "ok"
    # queue size above threshold
    for _ in range(5): q.put(1)
    start = time.time()
    res = process(q)
    elapsed = time.time() - start
    assert res == "ok"
    assert elapsed >= 0.01

def test_watermark_event_time():
    events = [{'timestamp': t} for t in [10, 20, 30]]
    tagged = watermark_event_time(events, 5)
    assert all('watermark' in e and 'is_late' in e for e in tagged)
    # watermark = 30 -5 =25, so 10,20 late; 30 on-time
    lates = [e['is_late'] for e in tagged]
    assert lates == [True, True, False]

def test_halt_on_error_and_skip_error(tmp_path, caplog):
    @halt_on_error
    def f1(x):
        raise ValueError("fail")
    with pytest.raises(ValueError):
        f1(1)
    caplog.set_level(logging.WARNING)
    @skip_error
    def f2(x):
        raise KeyError("oops")
    assert f2(1) is None
    assert "Skipping error" in caplog.text

def test_setup_logging():
    logger = setup_logging(logging.DEBUG)
    assert logger.level == logging.DEBUG
    # calling again shouldn't add handlers
    before = len(logger.handlers)
    logger2 = setup_logging()
    assert len(logger2.handlers) == before

def test_parallelize_stages():
    def s1(data): return data+1
    def s2(data): return data*2
    stages = {'inc': s1, 'dbl': s2}
    res = parallelize_stages(stages, 3)
    assert res['inc'] == 4
    assert res['dbl'] == 6

def test_track_lineage():
    lineage_store.clear()
    @track_lineage
    def transform(rec):
        rec['value'] = rec.get('value', 0) + 1
        return rec
    r = {'id':'x','value':0}
    out = transform(r)
    assert out['value'] == 1
    assert lineage_store['x'] == ['transform']
    # calling again adds another step
    transform(r)
    assert lineage_store['x'] == ['transform','transform']

def run_cli(argv):
    sys_argv = sys.argv
    sys.argv = argv
    try:
        return cli_manage()
    finally:
        sys.argv = sys_argv

def test_cli_manage_audit(capsys):
    ret = run_cli(['prog','audit','--window_size','120'])
    captured = capsys.readouterr()
    assert "Running audit with window size 120" in captured.out
    assert ret == 0

def test_cli_manage_show_logs(capsys):
    ret = run_cli(['prog','show-logs'])
    captured = capsys.readouterr()
    assert "Displaying logs" in captured.out
    assert ret == 0

def test_cli_manage_deploy(capsys):
    ret = run_cli(['prog','deploy-rules','--rule-file','rules.json'])
    captured = capsys.readouterr()
    assert "Deploying rules from rules.json" in captured.out
    assert ret == 0
