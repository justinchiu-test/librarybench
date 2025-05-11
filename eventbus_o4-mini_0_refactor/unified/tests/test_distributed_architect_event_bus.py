import pytest
import json
import threading
from distributed_architect.event_bus import EventBus, BufferError
import distributed_architect.jsonschema as jsonschema

def test_generate_documentation_empty():
    bus = EventBus()
    docs = bus.generateDocumentation()
    assert isinstance(docs, dict)
    assert docs['serializers'] == ['json']
    assert docs['acls'] == {}
    assert docs['metrics'] == []

def test_encrypt_payload_symmetry():
    bus = EventBus()
    original = "hello world"
    key = b'k'
    encrypted = bus.encryptPayload(original, key=key)
    # encrypt again with same key returns original bytes
    decrypted = bus.encryptPayload(encrypted, key=key)
    assert decrypted == original.encode('utf-8')

def test_default_serializer():
    bus = EventBus()
    data = {'a': 1}
    s = bus.serialize('json', data)
    assert isinstance(s, str)
    obj = bus.deserialize('json', s)
    assert obj == data

def test_custom_serializer():
    bus = EventBus()
    def enc(x): return f"enc:{x}"
    def dec(x): return x.replace("enc:", "")
    bus.registerSerializer('custom', enc, dec)
    assert 'custom' in bus.generateDocumentation()['serializers']
    out = bus.serialize('custom', 'data')
    assert out == 'enc:data'
    obj = bus.deserialize('custom', out)
    assert obj == 'data'

def test_authorization():
    bus = EventBus()
    assert not bus.checkAuthorization('topic1', 'alice')
    bus.authorizeActor('topic1', 'alice')
    assert bus.checkAuthorization('topic1', 'alice')
    assert not bus.checkAuthorization('topic1', 'bob')

def test_context_propagation():
    bus = EventBus()
    bus.propagateContext('trace_id', 'xyz')
    assert bus.getContext('trace_id') == 'xyz'
    # ensure thread-local isolation
    results = {}
    def worker():
        results['inner'] = bus.getContext('trace_id')
    t = threading.Thread(target=worker)
    t.start()
    t.join()
    assert results['inner'] is None

def test_balance_load_even():
    bus = EventBus()
    handlers = ['h1', 'h2']
    events = list(range(4))
    dist = bus.balanceLoad(handlers, events)
    assert dist == {'h1': [0,2], 'h2': [1,3]}

def test_balance_load_no_handlers():
    bus = EventBus()
    assert bus.balanceLoad([], [1,2,3]) == {}

def test_validate_schema_success():
    bus = EventBus()
    schema = {"type": "object", "properties": {"x": {"type": "number"}}, "required": ["x"]}
    payload = {"x": 10}
    assert bus.validateSchema(schema, payload)

def test_validate_schema_failure():
    bus = EventBus()
    schema = {"type": "object", "properties": {"x": {"type": "number"}}, "required": ["x"]}
    payload = {"x": "bad"}
    with pytest.raises(jsonschema.ValidationError):
        bus.validateSchema(schema, payload)

def test_backpressure_reject():
    bus = EventBus()
    bus.controlBackpressure(limit=2, policy='reject')
    bus.publish(1)
    bus.publish(2)
    with pytest.raises(BufferError):
        bus.publish(3)

def test_backpressure_drop_oldest():
    bus = EventBus()
    bus.controlBackpressure(limit=2, policy='drop_oldest')
    bus.publish('a')
    bus.publish('b')
    bus.publish('c')
    # queue should have 'b' and 'c'
    # we cannot access internal queue, but publishing next won't error
    bus.publish('d')

def test_clustering():
    bus = EventBus()
    bus.setupClustering(['n1', 'n2', 'n3'])
    assert bus.getLeader() == 'n1'
    assert bus.nodes == ['n1', 'n2', 'n3']
    with pytest.raises(ValueError):
        bus.setupClustering([])

def test_metrics_counter():
    bus = EventBus()
    assert bus.getCounter('hits') == 0
    bus.incrementCounter('hits')
    bus.incrementCounter('hits', 4)
    assert bus.getCounter('hits') == 5
    metrics = bus.exposeMetrics()
    assert 'hits' in metrics['counters']

def test_generate_documentation_full():
    bus = EventBus()
    bus.registerSerializer('custom', lambda x: x, lambda x: x)
    bus.authorizeActor('t1', 'u1')
    bus.incrementCounter('m1', 2)
    docs = bus.generateDocumentation()
    assert set(docs['serializers']) == {'json', 'custom'}
    assert docs['acls'] == {'t1': ['u1']}
    assert 'm1' in docs['metrics']
