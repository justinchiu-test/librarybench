import pytest
import json
from sdk.eventbus import EventBusSDK, AuthenticationError, BackpressureError
from jsonschema import ValidationError

def test_generate_client_sdk():
    sdk = EventBusSDK()
    swift, kotlin = sdk.generateClientSDK()
    assert "Swift" in swift
    assert "Kotlin" in kotlin

def test_encrypt_decrypt_payload():
    sdk = EventBusSDK()
    key = b"secret"
    original = b"hello world"
    encrypted = sdk.encryptPayload(original, key)
    assert encrypted != original
    decrypted = sdk.decryptPayload(encrypted, key)
    assert decrypted == original

def test_register_and_use_serializer_json():
    sdk = EventBusSDK()
    sdk.registerSerializer("json", lambda obj: json.dumps(obj).encode(), lambda b: json.loads(b.decode()))
    data = {"a": 1}
    ser = sdk.serialize("json", data)
    deser = sdk.deserialize("json", ser)
    assert deser == data

def test_serialize_unknown_serializer():
    sdk = EventBusSDK()
    with pytest.raises(KeyError):
        sdk.serialize("none", {})

def test_authenticate_user_success_and_failure():
    sdk = EventBusSDK()
    token = "token123"
    sdk.addValidToken(token)
    assert sdk.authenticateUser(token) is True
    with pytest.raises(AuthenticationError):
        sdk.authenticateUser("bad_token")

def test_propagate_context():
    sdk = EventBusSDK()
    payload = {"msg": "hi"}
    result = sdk.propagateContext(payload, correlation_id="cid", user_id="uid", performance_marks={"t": 1})
    assert result["payload"] == payload
    assert result["context"]["correlation_id"] == "cid"
    assert result["context"]["user_id"] == "uid"
    assert result["context"]["performance_marks"] == {"t": 1}

def test_balance_load_round_robin():
    sdk = EventBusSDK()
    # first even -> local, second odd -> remote, third -> local
    m1 = sdk.balanceLoad("m1")
    m2 = sdk.balanceLoad("m2")
    m3 = sdk.balanceLoad("m3")
    assert m1[0] == "local"
    assert m2[0] == "remote"
    assert m3[0] == "local"
    assert m1[1] == "m1"

def test_validate_and_register_schema():
    sdk = EventBusSDK()
    schema = {"type": "object", "properties": {"x": {"type": "number"}}, "required": ["x"]}
    sdk.registerSchema("topic1", schema)
    assert sdk.validateSchema("topic1", {"x": 10}) is True
    with pytest.raises(ValidationError):
        sdk.validateSchema("topic1", {"y": 5})

def test_control_backpressure_drop_and_block():
    sdk = EventBusSDK()
    sdk.queue_max_size = 2
    sdk.drop_policy = True
    assert sdk.controlBackpressure("a") is True
    assert sdk.controlBackpressure("b") is True
    # third message should be dropped
    assert sdk.controlBackpressure("c") is False
    # now block policy
    sdk.drop_policy = False
    # queue still full
    with pytest.raises(BackpressureError):
        sdk.controlBackpressure("d")

def test_setup_clustering_and_send_via_cluster():
    sdk = EventBusSDK()
    endpoints = ["fail", "ok"]
    sdk.setupClustering(endpoints)
    def sender(ep, msg):
        if ep == "fail":
            raise Exception("down")
        return f"sent to {ep}: {msg}"
    res = sdk.sendViaCluster("hello", sender)
    assert res == "sent to ok: hello"
    # if all fail
    sdk.setupClustering(["fail1", "fail2"])
    with pytest.raises(RuntimeError):
        sdk.sendViaCluster("hi", lambda e, m: (_ for _ in ()).throw(Exception("no")))

def test_expose_metrics_counters_and_histograms():
    sdk = EventBusSDK()
    sdk.exposeMetrics("requests")
    sdk.exposeMetrics("requests")
    assert sdk.counters["requests"] == 2
    sdk.exposeMetrics("latency", 0.123)
    sdk.exposeMetrics("latency", 0.456)
    assert sdk.histograms["latency"] == [0.123, 0.456]
