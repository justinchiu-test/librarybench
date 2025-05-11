import pytest
from healthcare_architect.event_bus import EventBus, Event

# Dummy crypto module
class DummyCrypto:
    def encrypt(self, data):
        return f"enc({data})"
    def decrypt(self, data):
        if data.startswith("enc(") and data.endswith(")"):
            return data[4:-1]
        return data

# Dummy serializer
class JsonSerializer:
    def serialize(self, event):
        return f"{event.id}:{event.payload}"

def test_subscribe_wildcard_star():
    bus = EventBus()
    results = []
    def handler(ev):
        results.append(ev.id)
    bus.subscribeWildcard('device.*.ward1', handler)
    ev = Event('1', 'data', 'device.sensor.ward1')
    bus.publish(ev, ev.routing_key)
    assert results == ['1']

def test_subscribe_wildcard_hash():
    bus = EventBus()
    results = []
    def handler(ev):
        results.append(ev.id)
    bus.subscribeWildcard('#', handler)
    ev1 = Event('1', 'd1', 'a.b.c')
    ev2 = Event('2', 'd2', 'x.y')
    bus.publish(ev1, ev1.routing_key)
    bus.publish(ev2, ev2.routing_key)
    assert results == ['1', '2']

def test_route_to_dead_letter_missing_payload():
    bus = EventBus()
    ev = Event('1', None, 'a.b')
    bus.publish(ev, ev.routing_key)
    assert len(bus.dead_letter_queue) == 1
    assert bus.dead_letter_queue[0]['reason'] == 'missing_payload'

def test_route_to_dead_letter_handler_exception():
    bus = EventBus()
    def bad_handler(ev):
        raise RuntimeError("fail")
    bus.subscribeWildcard('#', bad_handler)
    ev = Event('1', 'data', 'a.b')
    bus.publish(ev, ev.routing_key)
    assert len(bus.dead_letter_queue) == 1
    assert bus.dead_letter_queue[0]['reason'] == 'handler_exception'

def test_encrypt_event():
    bus = EventBus()
    crypto = DummyCrypto()
    bus.registerCryptoModule(crypto)
    results = []
    bus.subscribeWildcard('#', lambda ev: results.append(ev.payload))
    ev = Event('1', 'secret', 'a.b')
    bus.publish(ev, ev.routing_key)
    assert results == ['enc(secret)']

def test_apply_backpressure_drop_oldest():
    bus = EventBus()
    bus.applyBackpressure(limit=2, policy='drop_oldest')
    ev1 = Event('1', 'd1', 'a.b')
    ev2 = Event('2', 'd2', 'a.b')
    ev3 = Event('3', 'd3', 'a.b')
    bus.publish(ev1, ev1.routing_key)
    bus.publish(ev2, ev2.routing_key)
    bus.publish(ev3, ev3.routing_key)
    ids = [e.id for e in bus.queue]
    assert ids == ['2', '3']

def test_apply_backpressure_reject():
    bus = EventBus()
    bus.applyBackpressure(limit=2, policy='reject')
    ev1 = Event('1', 'd1', 'a.b')
    ev2 = Event('2', 'd2', 'a.b')
    ev3 = Event('3', 'd3', 'a.b')
    bus.publish(ev1, ev1.routing_key)
    bus.publish(ev2, ev2.routing_key)
    bus.publish(ev3, ev3.routing_key)
    ids = [e.id for e in bus.queue]
    assert ids == ['1', '2']

def test_register_serializer_and_serialize():
    bus = EventBus()
    ser = JsonSerializer()
    bus.registerSerializer('json', ser)
    ev = Event('1', 'data', 'x.y')
    output = bus.serialize('json', ev)
    assert output == '1:data'
    with pytest.raises(ValueError):
        bus.serialize('xml', ev)

def test_batch_publish():
    bus = EventBus()
    results = []
    bus.subscribeWildcard('#', lambda ev: results.append(ev.id))
    evs = [Event(str(i), f'd{i}', 'a.b') for i in range(3)]
    bus.batchPublish(evs)
    assert results == ['0', '1', '2']

def test_update_config_at_runtime():
    bus = EventBus()
    bus.updateConfigAtRuntime(backpressure_limit=5, backpressure_policy='reject', timeout=30)
    assert bus.backpressure_limit == 5
    assert bus.backpressure_policy == 'reject'
    assert bus.config['timeout'] == 30

def test_cluster_deploy_and_replication():
    bus = EventBus()
    ev = Event('1', 'data', 'a.b')
    bus.publish(ev, ev.routing_key)
    bus.clusterDeploy(['node1', 'node2'])
    assert bus.cluster['leader'] == 'node1'
    assert 'node1' in bus.cluster['replicated_stores']
    assert bus.cluster['replicated_stores']['node2'][0].id == '1'

def test_persist_and_replay():
    bus = EventBus()
    ev1 = Event('1', 'd1', 'a.b')
    ev2 = Event('2', 'd2', 'a.b')
    bus.publish(ev1, ev1.routing_key)
    bus.publish(ev2, ev2.routing_key)
    all_events = bus.persistAndReplay()
    assert len(all_events) == 2
    one_event = bus.persistAndReplay(start_index=1)
    assert len(one_event) == 1
    assert one_event[0].id == '2'

def test_register_extension_modifies_event():
    bus = EventBus()
    def ext(ev):
        ev.payload = ev.payload.upper()
        return ev
    bus.registerExtension(ext)
    results = []
    bus.subscribeWildcard('#', lambda ev: results.append(ev.payload))
    ev = Event('1', 'lower', 'a.b')
    bus.publish(ev, ev.routing_key)
    assert results == ['LOWER']
