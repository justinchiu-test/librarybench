import pytest
import time
from microservice_owner.event_bus import EventBus

def test_register_and_serialize():
    bus = EventBus()
    bus.registerSerializer('json', lambda o: str(o), lambda s: int(s))
    data = {'value': 123}
    serialized = bus.serialize('json', data['value'])
    assert serialized == '123'
    deserialized = bus.deserialize('json', serialized)
    assert deserialized == 123

def test_propagate_context():
    bus = EventBus()
    def func(x):
        return bus.context.data['key'] + x
    result = bus.propagateContext({'key': 5}, func, 10)
    assert result == 15
    assert getattr(bus.context, 'data', None) is None

def test_persist_and_replay():
    bus = EventBus()
    called = []
    def handler(evt):
        called.append(evt)
    bus.registerHandler('topic1', handler)
    bus.persistEvents(True, replay_mode=False)
    bus.publishSync('topic1', 'event1')
    assert bus.persistent_store == [('topic1', 'event1', None)]
    # replay without replay_mode should do nothing
    called.clear()
    bus.replay()
    assert called == []
    # enable replay and replay
    bus.persistEvents(True, replay_mode=True)
    called.clear()
    bus.replay()
    time.sleep(0.1)
    assert 'event1' in called

def test_publish_sync_and_async():
    bus = EventBus()
    result = []
    def handler(evt):
        result.append(evt * 2)
    bus.registerHandler('double', handler)
    bus.publishSync('double', 3)
    assert result == [6]
    result.clear()
    bus.publish('double', 4, async_=True)
    time.sleep(0.1)
    assert result == [8]

def test_report_health():
    bus = EventBus()
    bus.registerHandler('a', lambda x: x)
    bus.registerHandler('a', lambda x: x)
    health = bus.reportHealth()
    assert 'thread_pool_max_workers' in health
    assert health['queue_size'] == 0
    assert health['handler_counts']['a'] == 2

def test_balance_load_round_robin():
    bus = EventBus()
    reps = ['r1', 'r2', 'r3']
    picks = [bus.balanceLoad('t', reps) for _ in range(6)]
    assert picks == ['r1', 'r2', 'r3', 'r1', 'r2', 'r3']

def test_balance_load_weighted():
    bus = EventBus()
    reps = ['a', 'b']
    weights = [1, 2]
    picks = [bus.balanceLoad('w', reps, weights) for _ in range(3)]
    assert picks.count('a') == 1
    assert picks.count('b') == 2

def test_update_config():
    bus = EventBus()
    bus.updateConfig(timeout=5, backpressure=True)
    assert bus.config['timeout'] == 5
    assert bus.config['backpressure'] == True

def test_register_extension():
    bus = EventBus()
    ext_calls = []
    def ext(t, e):
        ext_calls.append((t, e))
    bus.registerExtension(ext)
    bus.publishSync('x', 'y')
    assert ext_calls == [('x', 'y')]

def test_authenticate_and_acl():
    bus = EventBus()
    bus.authenticate('sec', 'tok1')
    bus.registerHandler('sec', lambda e: None)
    with pytest.raises(PermissionError):
        bus.publishSync('sec', 'e1', token='bad')
    # valid token should not raise
    bus.publishSync('sec', 'e2', token='tok1')

def test_handle_errors_and_poison():
    bus = EventBus()
    calls = []
    def flaky(e):
        calls.append(e)
        if len(calls) < 3:
            raise ValueError("fail")
    bus.registerHandler('f', flaky)
    bus.publishSync('f', 'evt')
    # Should have retried up to max and then poison
    assert len(calls) == 3
    assert bus.poison_queue[-1][1] == 'evt'
