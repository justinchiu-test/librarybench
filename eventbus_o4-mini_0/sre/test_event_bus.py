import pytest
import time
import contextvars
from event_bus import EventBus

@pytest.fixture
def bus():
    bus = EventBus(max_workers=2, retry_attempts=2)
    bus.addToken('valid-token')
    yield bus
    bus.shutdown()

def test_authentication(bus):
    with pytest.raises(PermissionError):
        bus.publish({'data': 'x', 'token': 'invalid'}, sync=True)
    with pytest.raises(PermissionError):
        bus.subscribe(lambda e: None, token='invalid')
    # valid token works
    bus.subscribe(lambda e: None, token='valid-token')

def test_subscribe_and_sync_publish(bus):
    results = []
    def handler(event):
        results.append(event['data'])
    bus.subscribe(handler, token='valid-token')
    bus.publishSync({'data': 123, 'token': 'valid-token'})
    assert results == [123]

def test_async_publish_and_report_health(bus):
    results = []
    def handler(event):
        time.sleep(0.05)
        results.append(event['data'])
    bus.subscribe(handler, token='valid-token')
    initial = bus.reportHealth()
    assert initial['thread_pool_size'] == 2
    assert initial['queue_depth'] == 0
    assert initial['handler_count'] == 1
    # publish async
    for i in range(3):
        bus.publish({'data': i, 'token': 'valid-token'}, sync=False)
    # give tasks time to start
    time.sleep(0.01)
    mid = bus.reportHealth()
    assert mid['queue_depth'] >= 0
    # wait for completion
    time.sleep(0.2)
    assert sorted(results) == [0,1,2]
    final = bus.reportHealth()
    assert final['queue_depth'] == 0

def test_persistence(bus):
    bus.persistEvents(True)
    bus.subscribe(lambda e: None, token='valid-token')
    bus.publishSync({'data': 'a', 'token': 'valid-token'})
    bus.publish({'data': 'b', 'token': 'valid-token'})
    time.sleep(0.01)
    assert bus.persistent_storage == [{'data': 'a', 'token': 'valid-token'},
                                      {'data': 'b', 'token': 'valid-token'}]

def test_serializers(bus):
    def encode(event): return str(event).encode('utf-8')
    def decode(blob): return eval(blob.decode('utf-8'))
    bus.registerSerializer('test', encode, decode)
    assert 'test' in bus.serializers
    e = {'k': 'v'}
    blob = bus.serializers['test'][0](e)
    assert isinstance(blob, bytes)
    obj = bus.serializers['test'][1](blob)
    assert obj == e

def test_update_config(bus):
    bus.updateConfig(max_workers=3, retry_attempts=5)
    health = bus.reportHealth()
    assert health['thread_pool_size'] == 3
    assert bus.config['retry_attempts'] == 5

def test_extensions(bus):
    ext = lambda x: x
    bus.registerExtension(ext)
    assert ext in bus.extensions

def test_handle_errors_and_dead_letter(bus):
    calls = {'count': 0}
    def bad_handler(event):
        calls['count'] += 1
        raise ValueError("fail")
    wrapped = bus.handleErrors(bad_handler)
    bus.subscribe(wrapped, token='valid-token')
    # Publish sync to trigger retries
    bus.publishSync({'data': 'd', 'token': 'valid-token'})
    # Since retry_attempts=2, attempts=2 then dead-letter
    assert calls['count'] == 2
    assert bus.dead_letter == [{'data': 'd', 'token': 'valid-token'}]

def test_balance_load(bus):
    assert bus.balanceLoad() is True

def test_propagate_context(bus):
    var = contextvars.ContextVar('x', default=0)
    def set_and_get(event):
        return var.get()
    @bus.propagateContext
    def task():
        var.set(5)
        return var.get()
    # Outside context, default
    assert var.get() == 0
    # In propagated context, should get 5
    val = task()
    assert val == 5
    # Outer context unchanged
    assert var.get() == 0
