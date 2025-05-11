import pytest
import time
from trading_analyst.event_bus import EventBus

@pytest.fixture
def bus():
    return EventBus()

def test_generate_stubs(bus):
    stubs = bus.generate_stubs()
    assert 'cpp' in stubs and 'java' in stubs and 'python' in stubs
    assert stubs['cpp'].startswith('// C++')
    assert stubs['python'].startswith('# Python')

def test_encrypt_payload(bus):
    original = "SECRET"
    encrypted = bus.encrypt_payload(original, key='A')
    # decrypt by reapplying same key
    decrypted = bus.encrypt_payload(encrypted, key='A')
    assert decrypted == original

def test_register_and_use_serializer(bus):
    def ser(x): return x.upper()
    def deser(x): return x.lower()
    bus.register_serializer('test', ser, deser)
    assert 'test' in bus.serializers
    assert bus.serializers['test']['serializer']("abc") == "ABC"
    assert bus.serializers['test']['deserializer']("ABC") == "abc"

def test_authenticate_actor(bus):
    assert bus.authenticate_actor('valid_token') is True
    assert bus.authenticate_actor('invalid') is False

def test_propagate_context(bus):
    event = {}
    context = {'correlation_id': 'cid123', 'trace_span': 'span456'}
    out = bus.propagate_context(event, context)
    assert out['correlation_id'] == 'cid123'
    assert out['trace_span'] == 'span456'
    assert isinstance(out['timestamp'], float)

def test_balance_load(bus):
    items = ['a','b','c','d']
    handlers = ['h1','h2']
    assign = bus.balance_load(items, handlers)
    assert assign == {'h1': ['a','c'], 'h2': ['b','d']}

def test_validate_schema(bus):
    data = {'f1': 1, 'f2': 2}
    schema = {'fields': ['f1','f2']}
    assert bus.validate_schema(data, schema) is True
    bad_schema = {'fields': ['f1','f3']}
    assert bus.validate_schema(data, bad_schema) is False

def test_control_backpressure(bus):
    bus.queue = [1,2,3,4,5]
    out = bus.control_backpressure(limit=3)
    assert out == [3,4,5]
    # when under limit
    bus.queue = [1,2]
    out2 = bus.control_backpressure(limit=5)
    assert out2 == [1,2]

def test_setup_clustering(bus):
    nodes = ['n1','n2','n3']
    cluster = bus.setup_clustering(nodes)
    assert cluster['leader'] == 'n1'
    assert cluster['followers'] == ['n2','n3']
    empty = bus.setup_clustering([])
    assert empty['leader'] is None
    assert empty['followers'] == []

def test_expose_metrics(bus):
    bus.metrics['event_rate'] = 100
    bus.metrics['queue_latency'].append(0.5)
    m = bus.expose_metrics()
    assert m['event_rate'] == 100
    assert 0.5 in m['queue_latency']
    # original metrics unchanged
    bus.metrics['event_rate'] = 200
    assert m['event_rate'] == 100
