import pytest
import time
import asyncio
import backup_manager

@pytest.fixture(autouse=True)
def clear_state():
    backup_manager._callbacks.clear()
    backup_manager._rate_limits.clear()
    backup_manager._debounce_intervals.clear()
    backup_manager._last_execution_times.clear()
    backup_manager._event_log.clear()
    backup_manager._retry_policy = {'max_retries': 4, 'backoff_strategy': 'exponential'}
    backup_manager._polling_strategy = None
    yield

def test_register_and_unregister_callback():
    watcher = backup_manager.watch_directory(['/tmp'])
    calls = []
    def handler(event_type, path):
        calls.append((event_type, path))
    cb_id = backup_manager.register_callback("*.txt", handler)
    watcher.push_event('create', '/tmp/file.txt')
    watcher.push_event('create', '/tmp/file.log')
    assert calls == [('create', '/tmp/file.txt')]
    backup_manager.unregister_callback(cb_id)
    watcher.push_event('create', '/tmp/file.txt')
    assert calls == [('create', '/tmp/file.txt')]

def test_rate_limit():
    watcher = backup_manager.watch_directory(['/'])
    calls = []
    def handler(event_type, path):
        calls.append(path)
    cb_id = backup_manager.register_callback("*", handler)
    backup_manager.configure_rate_limit(cb_id, max_events_per_sec=2)
    t0 = time.time()
    watcher.push_event('modify', '/file1', timestamp=t0)
    watcher.push_event('modify', '/file2', timestamp=t0)
    watcher.push_event('modify', '/file3', timestamp=t0)
    assert len(calls) == 2

def test_priority_order():
    watcher = backup_manager.watch_directory(['/'])
    order = []
    def handler_a(e, p):
        order.append('A')
    def handler_b(e, p):
        order.append('B')
    cb1 = backup_manager.register_callback("*", handler_b, priority=10)
    cb2 = backup_manager.register_callback("*", handler_a, priority=1)
    watcher.push_event('create', '/x')
    assert order == ['A', 'B']

def test_debounce():
    watcher = backup_manager.watch_directory(['/'])
    calls = []
    def handler(e, p):
        calls.append((e, p, time.time()))
    cb_id = backup_manager.register_callback("*", handler)
    backup_manager.configure_debounce(cb_id, debounce_interval=0.5)
    t0 = time.time()
    watcher.push_event('modify', '/file', timestamp=t0)
    watcher.push_event('modify', '/file', timestamp=t0 + 0.1)
    watcher.push_event('modify', '/file', timestamp=t0 + 0.6)
    assert len(calls) == 2

def test_generate_change_summary():
    watcher = backup_manager.watch_directory(['/'])
    watcher.push_event('create', '/a')
    watcher.push_event('modify', '/b')
    watcher.push_event('move', '/c')
    watcher.push_event('delete', '/d')
    summary = backup_manager.generate_change_summary('midnight')
    assert summary == "3 files backed up, 1 deleted"
    summary2 = backup_manager.generate_change_summary('midnight')
    assert summary2 == "0 files backed up, 0 deleted"

def test_single_scan_with_custom_strategy():
    result = []
    def custom_scan(path):
        result.append(path)
        return ['file1', 'file2']
    backup_manager.set_polling_strategy(custom_scan)
    out = backup_manager.single_scan('/data')
    assert out == ['file1', 'file2']
    assert result == ['/data']

def test_retry_policy():
    watcher = backup_manager.watch_directory(['/'])
    calls = []
    state = {'cnt': 0}
    def handler(e, p):
        state['cnt'] += 1
        if state['cnt'] < 3:
            raise RuntimeError("fail")
        calls.append((e, p))
    backup_manager.set_retry_policy(max_retries=5)
    backup_manager.register_callback("*", handler)
    watcher.push_event('create', '/retry')
    # Should retry twice then succeed
    assert state['cnt'] == 3
    assert calls == [('create', '/retry')]

def test_async_watcher():
    aw = backup_manager.get_async_watcher()
    calls = []
    def handler(e, p):
        calls.append((e, p))
    backup_manager.register_callback("*.async", handler)
    async def run():
        await aw.push_event('delete', '/test.async')
    asyncio.run(run())
    assert calls == [('delete', '/test.async')]
