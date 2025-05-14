import os
import time
import tempfile
import threading
from filewatcher import (
    configure_thread_pool, set_filters, set_throttle,
    on_event, batch_dispatch, configure_logging,
    set_polling_strategy, apply_rate_limit,
    run_single_scan, get_watcher, Event
)

def test_configure_thread_pool():
    configure_thread_pool(5)
    w = get_watcher()
    assert w.worker_count == 5
    assert w.executor._max_workers == 5

def test_set_filters_and_scan(tmp_path):
    base = tmp_path / "assets"
    base.mkdir()
    # create files
    f1 = base / "a.png"; f1.write_text("img")
    f2 = base / "b.wav"; f2.write_text("audio")
    f3 = base / "c.psd.tmp"; f3.write_text("tmp")
    # configure filters
    set_filters(include=['**/*.png', '**/*.wav'], exclude=['**/*.psd.tmp'])
    res = run_single_scan(str(tmp_path))
    # expect only a.png and b.wav
    assert any(str(f1) in r for r in res)
    assert any(str(f2) in r for r in res)
    assert not any(str(f3) in r for r in res)

def test_set_throttle():
    set_throttle(100, 2000)
    w = get_watcher()
    assert w.max_events == 100
    assert w.per_ms == 2000

def test_on_event_and_emit():
    events = []
    def cb(evt):
        events.append(evt)
    on_event(cb)
    w = get_watcher()
    w._emit_event('modified', '/path/to/file')
    # give threads time
    time.sleep(0.1)
    assert len(events) == 1
    evt = events[0]
    assert evt.event_type == 'modified'
    assert evt.src_path == '/path/to/file'
    assert isinstance(evt.timestamp, float)

def test_batch_dispatch():
    events = []
    def cb(evt):
        events.append(evt)
    on_event(cb)
    w = get_watcher()
    batch_dispatch(50)
    # emit multiple events rapidly
    for i in range(3):
        w._emit_event('created', f'/file{i}')
        time.sleep(0.02)
    # wait for batch time
    time.sleep(0.1)
    # since batch dispatch groups, all should be called
    assert len(events) == 3
    batch_dispatch(None)  # reset

def test_configure_logging():
    configure_logging(logging_level:=10)
    w = get_watcher()
    assert w.logger.level == logging_level

def test_set_polling_strategy():
    def scanner(): pass
    set_polling_strategy(scanner)
    w = get_watcher()
    assert w.polling_strategy == scanner

def test_apply_rate_limit():
    apply_rate_limit('asset_loader', 30)
    w = get_watcher()
    assert w.rate_limits.get('asset_loader') == 30

def test_context_manager_start_stop():
    w = get_watcher()
    w.running = False
    with w as cm:
        assert cm.running
    assert not w.running
