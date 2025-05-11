import pytest
import json
import xml.etree.ElementTree as ET
from event_bus import EventBus
from jsonschema import ValidationError

# Fixtures
@pytest.fixture
def bus():
    eb = EventBus()
    # register serializers
    eb.register_serializer(
        "json",
        lambda data: json.dumps(data).encode("utf-8"),
        lambda b: json.loads(b.decode("utf-8"))
    )
    eb.register_serializer(
        "xml",
        lambda data: ET.tostring(ET.Element("root", data)),
        lambda b: ET.fromstring(b)
    )
    return eb

def test_generate_documentation(bus):
    docs = bus.generate_documentation()
    assert "openapi" in docs and "sdks" in docs
    assert "python" in docs["sdks"]

def test_encrypt_decrypt(bus):
    plaintext = b"patient data"
    ciphertext = bus.encrypt_payload(plaintext)
    assert isinstance(ciphertext, (bytes, bytearray))
    decrypted = bus.decrypt_payload(ciphertext)
    assert decrypted == plaintext

def test_serializer_json(bus):
    data = {"a": 1}
    bts = bus.serialize("json", data)
    obj = bus.deserialize("json", bts)
    assert obj == data

def test_serializer_xml(bus):
    data = {"id": "123", "name": "John"}
    bts = bus.serialize("xml", data)
    elem = bus.deserialize("xml", bts)
    assert elem.tag == "root"
    assert elem.attrib["id"] == "123"
    assert elem.attrib["name"] == "John"

def test_authorization(bus):
    bus.set_topic_scopes("lab_results", ["read"])
    token = bus.create_token("alice", ["read", "write"])
    assert bus.authorize_user(token, "lab_results")
    bad_token = bus.create_token("bob", ["write"])
    assert not bus.authorize_user(bad_token, "lab_results")

def test_propagate_context(bus):
    event = {"type": "lab"}
    ctx = {"patient_id": "p1", "consent": True}
    new_event = bus.propagate_context(event, ctx)
    assert new_event["_context"] == ctx
    assert new_event["type"] == "lab"

def test_balance_load(bus):
    bus.configure_workers("transforms", ["w1", "w2"])
    evt = {"x": 1}
    w1 = bus.balance_load("transforms", evt)
    w2 = bus.balance_load("transforms", evt)
    w3 = bus.balance_load("transforms", evt)
    assert w1 == "w1"
    assert w2 == "w2"
    assert w3 == "w1"

def test_validate_schema(bus):
    schema = {
        "type": "object",
        "properties": {"a": {"type": "number"}},
        "required": ["a"]
    }
    bus.register_schema("topic1", schema)
    assert bus.validate_schema("topic1", {"a": 5})
    assert not bus.validate_schema("topic1", {"b": 1})
    metrics = bus.expose_metrics()
    assert metrics["validation_errors"] == 1

def test_backpressure(bus):
    topic = "tp"
    bus.register_schema(topic, {})  # creates queue
    bus.set_backpressure(topic, max_size=1)
    # first pass
    bus.control_backpressure(topic)
    # second should overflow
    with pytest.raises(OverflowError):
        bus.control_backpressure(topic)

def test_clustering(bus):
    nodes = ["n1", "n2", "n3"]
    bus.setup_clustering(nodes)
    assert bus.cluster_nodes == nodes

def test_metrics(bus):
    # simulate some metrics
    bus.metrics_data["event_count"] = 10
    bus.metrics_data["processing_latencies"].append(0.123)
    met = bus.expose_metrics()
    assert met["event_count"] == 10
    assert 0.123 in met["processing_latencies"]
