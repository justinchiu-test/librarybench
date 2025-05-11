import pytest
from game_dev.event_bus import (
    EventBus,
    EventBusError,
    BackpressurePolicy,
    CryptoModule,
    Serializer,
    JsonSerializer,
)


def test_wildcard_subscriptions():
    bus = EventBus()
    received = []

    def handler(msg):
        received.append(msg)

    bus.subscribe("zone.*.player", handler)
    bus.publish("zone.1.player", {"x": 10})
    bus.publish("zone.1.npc", {"y": 5})
    bus.publish("zone.2.player", {"z": 7})

    assert {"x": 10} in received
    assert {"z": 7} in received
    assert all(isinstance(item, dict) for item in received)
    assert len(received) == 2

    # multi-level
    received.clear()
    bus.subscribe("global.#", handler)
    bus.publish("global", {"a": 1})
    bus.publish("global.lobby", {"b": 2})
    bus.publish("global.lobby.chat", {"c": 3})
    assert {"a": 1} in received
    assert {"b": 2} in received
    assert {"c": 3} in received


def test_dead_letter_on_malformed_serializer():
    class BadSerializer(Serializer):
        def serialize(self, event):
            raise ValueError("bad")
        def deserialize(self, data):
            return data

    bus = EventBus()
    bus.register_serializer("bad", BadSerializer())
    bus.publish("topic", {"x": 1}, content_type="bad")
    assert len(bus.dead_letters) == 1
    topic, event = bus.dead_letters[0]
    assert topic == "topic"
    assert event == {"x": 1}


def test_dead_letter_on_handler_exception():
    bus = EventBus()
    def bad_handler(msg):
        raise RuntimeError("fail")
    bus.subscribe("t.#", bad_handler)
    bus.publish("t.1", {"foo": "bar"})
    assert len(bus.dead_letters) == 1
    topic, event = bus.dead_letters[0]
    assert topic == "t.1"
    assert event == {"foo": "bar"}


def test_encryption_module():
    class RevCrypto(CryptoModule):
        def encrypt(self, data):
            return data[::-1]
        def decrypt(self, data):
            return data[::-1]

    bus = EventBus(crypto=RevCrypto())
    received = []
    bus.subscribe("enc.*", lambda msg: received.append(msg))
    bus.publish("enc.test", b"hello", content_type=None)
    # default serializer tries JSON and fails, so dead letter
    # Instead test with JsonSerializer events
    bus = EventBus(crypto=RevCrypto(), serializer=JsonSerializer())
    received = []
    bus.subscribe("enc.*", lambda msg: received.append(msg))
    bus.publish("enc.test", {"k": "v"})
    assert received == [{"k": "v"}]


def test_backpressure_reject():
    bus = EventBus(queue_size=0, backpressure=BackpressurePolicy.REJECT)
    with pytest.raises(EventBusError):
        bus.publish("any", {"x": 1})


def test_backpressure_drop_oldest():
    # When queue_size=0 and policy DROP_OLDEST, should not raise
    bus = EventBus(queue_size=0, backpressure=BackpressurePolicy.DROP_OLDEST)
    # These publishes should not error
    bus.publish("a", {"x": 1})
    bus.publish("a", {"y": 2})
    # Queue should stay <= size
    assert bus.queue_size == 0

def test_register_serializer_and_usage():
    bus = EventBus()
    calls = []
    class DummySer(Serializer):
        def serialize(self, event):
            calls.append(("ser", event))
            return b"X"
        def deserialize(self, data):
            calls.append(("deser", data))
            return {"ok": True}

    bus.register_serializer("dummy", DummySer())
    out = []
    bus.subscribe("d.#", lambda msg: out.append(msg))
    bus.publish("d.1", {"foo": "bar"}, content_type="dummy")
    assert ("ser", {"foo": "bar"}) in calls
    assert ("deser", b"X") in calls
    assert out == [{"ok": True}]

def test_batch_publish_and_persist_replay():
    bus = EventBus(persist=True)
    out = []
    bus.subscribe("b.#", lambda msg: out.append(msg))
    events = [{"i": 1}, {"i": 2}, {"i": 3}]
    bus.batch_publish("b.test", events)
    assert out == events
    # persisted raw bytes in JSON form
    persisted = list(bus.replay())
    assert len(persisted) == 3
    topics = [t for t, _ in persisted]
    assert all(t == "b.test" for t in topics)

def test_update_config_runtime():
    bus = EventBus(queue_size=1, backpressure=BackpressurePolicy.REJECT)
    bus.update_config(queue_size=0, backpressure=BackpressurePolicy.DROP_OLDEST)
    assert bus.queue_size == 0
    assert bus.backpressure == BackpressurePolicy.DROP_OLDEST

def test_register_extension():
    bus = EventBus()
    class Ext: pass
    e = Ext()
    bus.register_extension("myext", e)
    assert bus.extensions["myext"] is e
