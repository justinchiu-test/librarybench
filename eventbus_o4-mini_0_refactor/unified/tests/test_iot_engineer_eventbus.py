import pytest
from iot_engineer.eventbus import IoTEventBus

class DummyCrypto:
    def encrypt(self, data):
        return f"encrypted({data})"
    def decrypt(self, data):
        if data.startswith("encrypted(") and data.endswith(")"):
            return data[len("encrypted("):-1]
        return data

class DummySerializer:
    def serialize(self, obj):
        return str(obj).encode()
    def deserialize(self, data):
        return data.decode()

def test_register_and_generate_stubs():
    bus = IoTEventBus()
    bus.registerSerializer("cbor", DummySerializer())
    bus.registerSerializer("protobuf", DummySerializer())
    stubs = bus.generateStubs()
    assert "cbor" in stubs and "protobuf" in stubs
    assert stubs["cbor"].startswith("# Stub for serializer 'cbor'")

def test_encrypt_payload_without_module():
    bus = IoTEventBus()
    payload = {"temp": 22}
    assert bus.encryptPayload(payload) == payload

def test_encrypt_payload_with_module():
    bus = IoTEventBus()
    crypto = DummyCrypto()
    bus.setEncryptionModule(crypto)
    payload = "{'data': 123}"
    encrypted = bus.encryptPayload(payload)
    assert encrypted == "encrypted({'data': 123})"

def test_authorize_device():
    bus = IoTEventBus()
    device_id = "dev1"
    token = "token123"
    bus.registerDeviceToken(device_id, token)
    assert bus.authorizeDevice(device_id, token)
    assert not bus.authorizeDevice(device_id, "wrong")

def test_propagate_context():
    bus = IoTEventBus()
    event = {"value": 10}
    context = {"location": "field"}
    new_event = bus.propagateContext(event, context)
    assert event.get("context") is None  # original unchanged
    assert new_event["context"] == context
    assert new_event["value"] == 10

def test_balance_load_and_dispatch():
    bus = IoTEventBus()
    results = []
    def handler_a(evt): results.append(("a", evt))
    def handler_b(evt): results.append(("b", evt))
    bus.balanceLoad(handler_a)
    bus.balanceLoad(handler_b)
    # Dispatch multiple events and expect round-robin
    for i in range(4):
        evt = {"id": i}
        h = bus.dispatchEvent(evt)
        assert h in (handler_a, handler_b)
    # Check order
    assert results == [
        ("a", {"id": 0}),
        ("b", {"id": 1}),
        ("a", {"id": 2}),
        ("b", {"id": 3}),
    ]
    assert bus.event_count == 4

def test_schema_validation():
    bus = IoTEventBus()
    bus.setSchema({"a": int, "b": str})
    assert bus.validateSchema({"a": 1, "b": "x"})
    assert not bus.validateSchema({"a": "wrong", "b": "x"})
    assert not bus.validateSchema({"a": 1})

def test_backpressure_queue_limits():
    bus = IoTEventBus(max_queue_size=3)
    # fill beyond capacity
    for i in range(5):
        bus.dispatchEvent({"n": i})
    # Since deque maxlen=3, only last 3 remain
    assert bus.controlBackpressure() == 3

def test_clustering_setup():
    bus = IoTEventBus()
    nodes = ["node1", "node2", "node3"]
    bus.setupClustering(nodes)
    assert bus.cluster_nodes == nodes
    # modify original list should not affect bus
    nodes.append("node4")
    assert bus.cluster_nodes == ["node1", "node2", "node3"]

def test_metrics_and_latency():
    bus = IoTEventBus()
    # Initially zero
    m = bus.exposeMetrics()
    assert m["event_count"] == 0
    assert m["queue_length"] == 0
    assert m["average_latency"] == 0
    # record some events and latencies
    bus.dispatchEvent({"x": 1})
    bus.recordLatency(100)
    bus.dispatchEvent({"x": 2})
    bus.recordLatency(200)
    metrics = bus.exposeMetrics()
    assert metrics["event_count"] == 2
    assert metrics["queue_length"] == 2  # two dispatched, none removed
    assert pytest.approx(metrics["average_latency"], rel=1e-3) == 150.0
