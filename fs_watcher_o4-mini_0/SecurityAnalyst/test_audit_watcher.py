import pytest
import tempfile
import os
import time
import threading
import asyncio
from audit_watcher import (
    watch_directory, register_callback, unregister_callback,
    configure_rate_limit, generate_change_summary, single_scan,
    set_retry_policy, get_async_watcher, _summary_counts, _callbacks
)

def test_register_and_unregister():
    def handler(event): pass
    cid = register_callback(r".*\.conf$", handler, priority=10)
    assert cid in _callbacks
    unregister_callback(cid)
    assert cid not in _callbacks

def test_event_dispatch_and_summary():
    # clear previous
    _summary_counts.clear()
    events = []
    def handler(event):
        events.append(event)
    watcher = watch_directory(['/tmp'])
    cid = register_callback(r"/tmp/.*\.txt$", handler, priority=5)
    watcher.simulate_event('created', '/tmp/test.txt')
    watcher.simulate_event('deleted', '/tmp/test.txt')
    assert len(events) == 2
    summary = generate_change_summary('daily')
    assert "1 created" in summary
    assert "1 deleted" in summary
    unregister_callback(cid)

def test_rate_limit():
    events = []
    def handler(event):
        events.append(event)
    watcher = watch_directory(['/var/log'])
    cid = register_callback(r".*", handler)
    configure_rate_limit(handler, max_events_per_minute=2)
    # simulate 3 events quickly
    watcher.simulate_event('modified', '/var/log/a.log')
    watcher.simulate_event('modified', '/var/log/b.log')
    watcher.simulate_event('modified', '/var/log/c.log')
    assert len(events) == 2
    unregister_callback(cid)

def test_retry_policy():
    calls = []
    def flaky_handler(event):
        calls.append(time.time())
        raise ValueError("fail")
    watcher = watch_directory(['/etc'])
    cid = register_callback(r".*", flaky_handler)
    set_retry_policy(max_retries=2, backoff_strategy='none')
    start = time.time()
    watcher.simulate_event('modified', '/etc/passwd')
    # should have retried 2 times + initial = 3 calls
    assert len(calls) == 3
    unregister_callback(cid)

def test_single_scan(tmp_path):
    # create files
    d = tmp_path / "confdir"
    d.mkdir()
    f1 = d / "a.cfg"
    f1.write_text("data")
    f2 = d / "b.cfg"
    f2.write_text("more")
    result = single_scan(str(d))
    assert os.path.join(str(d), "a.cfg") in result
    assert os.path.join(str(d), "b.cfg") in result
    assert result[os.path.join(str(d), "a.cfg")] == 4

def test_async_watcher(loop):
    # setup
    events = []
    def handler(event):
        events.append(event)
    aw = get_async_watcher(loop)
    cid = register_callback(r".*", handler)
    event = {'type':'created','path':'/tmp/x','timestamp':time.time()}
    aw.dispatch(event)
    # allow loop to run
    time.sleep(0.1)
    assert len(events) == 1
    unregister_callback(cid)
