import os
import time
import shutil
import logging
import asyncio
import pytest
from fswatcher import (
    single_scan, register_callback, unregister_callback,
    configure_rate_limit, generate_change_summary,
    configure_logging, set_polling_strategy, watch_directory,
    FileEvent, set_retry_policy, get_async_watcher, _pollers
)

def test_register_and_unregister():
    def cb(e): pass
    cid = register_callback("*.txt", cb, priority=5)
    assert cid in __import__('fswatcher')._callbacks
    assert unregister_callback(cid) is True
    assert cid not in __import__('fswatcher')._callbacks

def test_single_scan_add_modify_delete(tmp_path):
    p = tmp_path / "file.txt"
    # initial scan: empty
    events = single_scan(tmp_path)
    assert events == []
    # add file
    p.write_text("hello")
    events = single_scan(tmp_path)
    assert len(events) == 1
    assert events[0].type == 'added'
    # modify file
    time.sleep(0.01)
    p.write_text("world")
    events = single_scan(tmp_path)
    assert len(events) == 1
    assert events[0].type == 'modified'
    # delete file
    p.unlink()
    events = single_scan(tmp_path)
    assert len(events) == 1
    assert events[0].type == 'deleted'

def test_rate_limit(tmp_path):
    configure_rate_limit(max_events=2, per_second=True)
    files = []
    for i in range(5):
        f = tmp_path / f"{i}.txt"
        f.write_text("x")
        files.append(f)
    ev = single_scan(tmp_path)
    assert len(ev) == 2
    # rest dropped
    ev2 = single_scan(tmp_path)
    assert ev2 == []

def test_generate_change_summary(tmp_path):
    # reset summary
    __import__('fswatcher')._summary_events.clear()
    p1 = tmp_path / "a.txt"
    p2 = tmp_path / "b.txt"
    p1.write_text("1")
    p2.write_text("2")
    single_scan(tmp_path)
    p1.write_text("3")
    single_scan(tmp_path)
    p2.unlink()
    single_scan(tmp_path)
    summary = generate_change_summary()
    assert summary['added'] == 2
    assert summary['modified'] == 1
    assert summary['deleted'] == 1

def test_configure_logging():
    logger = logging.getLogger("testlogger")
    configure_logging(logger, level=logging.INFO)
    from fswatcher import _logger
    assert _logger is logger
    assert _logger.level == logging.INFO

def test_set_polling_strategy():
    class DummyPoller: pass
    set_polling_strategy("dummy", DummyPoller)
    assert "dummy" in _pollers
    assert _pollers["dummy"] is DummyPoller

def test_retry_policy(tmp_path):
    logs = []
    counter = {'calls': 0}
    def failing_cb(evt):
        counter['calls'] += 1
        if counter['calls'] < 3:
            raise ValueError("fail")
        logs.append(evt.type)
    cid = register_callback("*.txt", failing_cb)
    set_retry_policy(retries=2, backoff='constant')
    p = tmp_path / "x.txt"
    p.write_text("1")
    ev = single_scan(tmp_path)
    assert counter['calls'] == 3  # 1 initial + 2 retries
    assert logs == ['added']
    unregister_callback(cid)

@pytest.mark.asyncio
async def test_async_watcher_empty(tmp_path):
    AsyncW = get_async_watcher()
    watcher = AsyncW(tmp_path, loop=asyncio.get_event_loop(), options={'interval': 0.01})
    count = 0
    async for ev in watcher:
        count += 1
    assert count == 0

def test_watch_directory(tmp_path):
    # Test that watch_directory returns a poller with stop method
    p = watch_directory(tmp_path, options={'interval':0.01})
    assert hasattr(p, 'stop')
    p.stop()
