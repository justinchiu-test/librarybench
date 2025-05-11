import os
import pytest
from observability_bus import ObservabilityEventBus, IdentityCrypto

# cleanup persist file before each test
@pytest.fixture(autouse=True)
def cleanup():
    fn = 'events.log'
    try:
        os.remove(fn)
    except:
        pass
    yield
    try:
        os.remove(fn)
    except:
        pass

def test_single_level_wildcard():
    bus = ObservabilityEventBus()
    received = []
    bus.subscribeWildcard('service.*.prod', lambda t,e: received.append((t,e)))
    bus.publish('service.auth.prod', {'msg': 'ok'})
    bus.process()
    assert received == [('service.auth.prod', {'msg': 'ok'})]

def test_multi_level_wildcard():
    bus = ObservabilityEventBus()
    received = []
    bus.subscribeWildcard('service.#', lambda t,e: received.append((t,e)))
    bus.publish('service.auth.us.prod', {'v': 1})
    bus.process()
    assert received == [('service.auth.us.prod', {'v': 1})]

def test_dead_letter_on_callback_exception():
    bus = ObservabilityEventBus()
    def cb(t,e):
        raise ValueError("fail")
    bus.subscribeWildcard('x.#', cb)
    bus.publish('x.test', {'a': 1})
    bus.process()
    assert len(bus.dead_letter_queue) == 1
    entry = bus.dead_letter_queue[0]
    assert entry['error'] == "fail"
    assert entry['topic'] == 'x.test'

def test_encryption_decryption():
    class ReverseCrypto:
        def encrypt(self, data):
            return data[::-1]
        def decrypt(self, data):
            return data[::-1]
    bus = ObservabilityEventBus()
    bus.registerCrypto(ReverseCrypto())
    received = []
    bus.subscribeWildcard('#', lambda t,e: received.append((t,e)))
    bus.publish('a.b', {'secure': 'data'}, encrypt=True)
    bus.process()
    assert received == [('a.b', {'secure': 'data'})]

def test_backpressure_drop_oldest():
    bus = ObservabilityEventBus({'queue_size': 1, 'backpressure_policy': 'drop_oldest'})
    received = []
    bus.subscribeWildcard('#', lambda t,e: received.append((t,e)))
    bus.publish('t1', {'n': 1})
    bus.publish('t2', {'n': 2})
    # queue should have only the second
    bus.process()
    assert received == [('t2', {'n': 2})]

def test_backpressure_reject():
    bus = ObservabilityEventBus({'queue_size': 1, 'backpressure_policy': 'reject'})
    received = []
    bus.subscribeWildcard('#', lambda t,e: received.append((t,e)))
    ok1 = bus.publish('x', {'v': 1})
    ok2 = bus.publish('y', {'v': 2})
    assert ok1 is True
    assert ok2 is False
    assert len(bus.dead_letter_queue) == 1
    assert bus.dead_letter_queue[0]['topic'] == 'y'

def test_register_serializer():
    class DumbSerializer:
        def serialize(self, event):
            return str(event['v'])
        def deserialize(self, data):
            return {'v': int(data)}
    bus = ObservabilityEventBus()
    bus.registerSerializer('dumb', DumbSerializer())
    received = []
    bus.subscribeWildcard('#', lambda t,e: received.append(e))
    bus.publish('p', {'v': 5}, serializer='dumb')
    bus.process()
    assert received == [{'v': 5}]

def test_batch_publish_and_flush():
    bus = ObservabilityEventBus({'batch_size': 2})
    received = []
    bus.subscribeWildcard('#', lambda t,e: received.append(e))
    bus.batchPublish('b', {'x': 1})
    assert received == []
    bus.batchPublish('b', {'x': 2})
    bus.process()
    assert received == [{'x': 1}, {'x': 2}]

def test_update_config_runtime():
    bus = ObservabilityEventBus()
    bus.updateConfigAtRuntime('queue_size', 2)
    assert bus.config['queue_size'] == 2
    # test that new size applies
    bus.publish('a', {'k':1})
    bus.publish('b', {'k':2})
    with pytest.raises(Exception):
        bus.config['backpressure_policy'] = 'reject'
        bus.publish('c', {'k':3})

def test_register_extension():
    def ext(event, topic):
        event['ext'] = True
        return event
    bus = ObservabilityEventBus()
    bus.registerExtension(ext)
    received = []
    bus.subscribeWildcard('#', lambda t,e: received.append(e))
    bus.publish('x', {'v': 10})
    bus.process()
    assert received[0]['ext'] is True

def test_persist_and_replay(tmp_path):
    fn = tmp_path / "test.log"
    bus = ObservabilityEventBus({'persist_file': str(fn)})
    bus.subscribeWildcard('#', lambda t,e: None)
    bus.publish('p1', {'a':1})
    bus.publish('p2', {'b':2})
    # replay with subscriber
    rec = []
    def sub(t,e):
        rec.append((t,e))
    events = bus.persistAndReplay(subscriber=sub, file=str(fn))
    assert rec == [('p1', {'a':1}), ('p2', {'b':2})]
    assert events == [{'topic':'p1','event':{'a':1}}, {'topic':'p2','event':{'b':2}}]

def test_cluster_deploy():
    bus = ObservabilityEventBus()
    leader = bus.clusterDeploy([3,1,2])
    assert leader == 1
    assert bus.leader == 1
    assert set(bus.cluster_nodes) == {1,2,3}
