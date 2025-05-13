import pytest
import logging
import time
import asyncio
import pipeline

@pytest.fixture(autouse=True)
def clear_state():
    # Clear callbacks
    with pipeline._callback_lock:
        pipeline._callbacks.clear()
    # Clear events
    pipeline._events.clear()
    # Clear rate limits
    with pipeline._rate_limit_lock:
        pipeline._rate_limits.clear()
    # Reset polling
    pipeline.set_polling_strategy(pipeline.DefaultPoller())
    # Reset retry policy
    pipeline.set_retry_policy(0, None)
    yield

def test_register_and_unregister_callback():
    calls = []
    def handler(evt):
        calls.append(evt)
    handler_id = pipeline.register_callback('*.txt', handler, priority=10)
    assert isinstance(handler_id, str)
    # Simulate an event
    evt = pipeline.Event('created', 'file.txt')
    pipeline._invoke_callbacks(evt)
    assert len(calls) == 1
    assert calls[0] is evt
    # Unregister
    assert pipeline.unregister_callback(handler_id)
    calls.clear()
    pipeline._invoke_callbacks(evt)
    assert calls == []
    # Unregister non-existent
    assert not pipeline.unregister_callback('nonexistent')

def test_rate_limit_enforcement():
    pipeline.configure_rate_limit('*.csv', max_events_per_sec=2)
    e1 = pipeline.Event('created', 'a.csv')
    e2 = pipeline.Event('created', 'b.csv')
    e3 = pipeline.Event('created', 'c.csv')
    assert pipeline._apply_rate_limit(e1)
    assert pipeline._apply_rate_limit(e2)
    # Third within same second should be dropped
    assert not pipeline._apply_rate_limit(e3)
    # After 1 second reset
    time.sleep(1.1)
    assert pipeline._apply_rate_limit(e3)

def test_generate_change_summary():
    now = time.time()
    # Old event outside period
    pipeline._events.append(pipeline.Event('created', 'old.csv', timestamp=now - 7200))
    # Recent events
    pipeline._events.append(pipeline.Event('created', 'new.csv', timestamp=now - 10))
    pipeline._events.append(pipeline.Event('moved', 'log.json', timestamp=now - 5))
    summary = pipeline.generate_change_summary('hourly')
    assert summary == "1 CSVs ingested, 1 JSON logs moved"

def test_set_and_get_retry_policy():
    pipeline.set_retry_policy(5, 'exponential')
    policy = pipeline.get_retry_policy()
    assert policy['max_retries'] == 5
    assert policy['backoff_strategy'] == 'exponential'

def test_configure_logging():
    logger = logging.getLogger('testlogger')
    # Remove existing handlers
    for h in list(logger.handlers):
        logger.removeHandler(h)
    pipeline.configure_logging(logger, level=logging.DEBUG)
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) >= 1

def test_single_scan_and_watch_directory():
    class DummyPoller:
        def __init__(self):
            self.called = False
        def poll(self, paths, recursive):
            if not self.called:
                self.called = True
                return [
                    {'event_type': 'created', 'path': 'first.csv', 'timestamp': time.time()},
                    {'event_type': 'moved', 'path': 'second.json', 'timestamp': time.time(), 'dest_path': 'dest.json'}
                ]
            return []
    dp = DummyPoller()
    pipeline.set_polling_strategy(dp)
    # Test single_scan
    results = pipeline.single_scan('/data')
    assert len(results) == 2
    assert results[0].src_path == 'first.csv'
    assert results[1].event_type == 'moved'
    # Test watch_directory (sync)
    watcher = pipeline.watch_directory('/data')
    evt1 = next(watcher)
    assert evt1.src_path == 'first.csv'
    evt2 = next(watcher)
    assert evt2.dest_path == 'dest.json'

@pytest.mark.asyncio
async def test_get_async_watcher():
    class DummyPoller:
        def __init__(self):
            self.called = False
        def poll(self, paths, recursive):
            if not self.called:
                self.called = True
                return [{'event_type': 'created', 'path': 'async.csv', 'timestamp': time.time()}]
            return []
    pipeline.set_polling_strategy(DummyPoller())
    aw = pipeline.get_async_watcher('/async')
    evt = await aw.next_event()
    assert evt.src_path == 'async.csv'
