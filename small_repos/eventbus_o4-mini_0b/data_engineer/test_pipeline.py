import pytest
import time
from etl.pipeline import ETLPipeline

class DummySerializer:
    def serialize(self, data):
        return f"<serialized>{data}</serialized>"
    def deserialize(self, data):
        return data.replace("<serialized>", "").replace("</serialized>", "")

def test_report_health_initial():
    p = ETLPipeline()
    health = p.reportHealth()
    assert health['consumer_lag'] == 0
    assert health['thread_pool_usage'] == 0
    assert health['handler_counts'] == {}

def test_register_serializer():
    p = ETLPipeline()
    serializer = DummySerializer()
    p.registerSerializer('dummy', serializer)
    assert 'dummy' in p.serializer_registry
    assert p.serializer_registry['dummy'] is serializer

def test_propagate_context():
    p = ETLPipeline()
    def process(merged):
        return merged
    context = {'trace_id': 123}
    wrapped = p.propagateContext(process, context)
    result = wrapped(1, key='value')
    assert result['context'] is context
    assert result['args'] == (1,)
    assert result['kwargs'] == {'key': 'value'}

def test_persist_events():
    p = ETLPipeline()
    p.persistEvents({'id': 1}, {'processed': True})
    assert p.event_store['raw'] == [{'id': 1}]
    assert p.event_store['processed'] == [{'processed': True}]

def test_publish_sync():
    p = ETLPipeline()
    serializer = DummySerializer()
    def process(e):
        return e * 2
    events = [1, 2, 3]
    p.publishSync(events, process, serializer)
    expected_raw = [serializer.serialize(e) for e in events]
    expected_processed = [process(e) for e in events]
    assert p.event_store['raw'] == expected_raw
    assert p.event_store['processed'] == expected_processed

def test_update_config_parallelism():
    p = ETLPipeline()
    old_executor = p._executor
    p.updateConfig(parallelism=2, timeout=10)
    assert p.config['parallelism'] == 2
    assert p.config['timeout'] == 10
    assert p._executor._max_workers == 2
    assert p._executor is not old_executor

def test_register_extension():
    p = ETLPipeline()
    ext = lambda x: x + 1
    p.registerExtension('plus_one', ext)
    assert p.extension_registry['plus_one'] is ext

def test_authenticate():
    p = ETLPipeline()
    token = 'token123'
    assert not p.authenticate(token)
    p.addToken(token)
    assert p.authenticate(token)

def test_handle_errors_success():
    p = ETLPipeline()
    calls = {'count': 0}
    def flaky(x):
        calls['count'] += 1
        if calls['count'] < 3:
            raise ValueError("fail")
        return x * 10
    wrapped = p.handleErrors(flaky, retries=5, initial_delay=0)
    result = wrapped(5)
    assert result == 50
    assert calls['count'] == 3
    assert p.dead_letter == []

def test_handle_errors_fail():
    p = ETLPipeline()
    def always_fail():
        raise RuntimeError("error")
    wrapped = p.handleErrors(always_fail, retries=2, initial_delay=0)
    with pytest.raises(RuntimeError):
        wrapped()
    assert len(p.dead_letter) == 1
    event = p.dead_letter[0]
    assert event['func'] == 'always_fail'
    assert event['args'] == ()
    assert event['kwargs'] == {}

def test_balance_load_and_report_health():
    p = ETLPipeline()
    def add(x, y):
        return x + y
    def mul(x, y):
        return x * y
    tasks = [
        (add, (1, 2), {}),
        (mul, (2, 3), {}),
        (add, (5, 6), {}),
    ]
    futures = p.balanceLoad(tasks)
    results = [f.result() for f in futures]
    assert set(results) == {3, 6, 11}
    health = p.reportHealth()
    assert health['handler_counts'] == {'add': 2, 'mul': 1}
    assert health['thread_pool_usage'] == p.config['parallelism']
