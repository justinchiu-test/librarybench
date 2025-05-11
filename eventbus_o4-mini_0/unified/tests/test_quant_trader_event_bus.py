import pytest
from quant_trader.event_bus import EventBus, SimpleJSONSerializer

class DummyCrypto:
    def encrypt(self, event):
        return f"enc({event})"
    def decrypt(self, payload):
        if payload.startswith("enc(") and payload.endswith(")"):
            return payload[4:-1]
        return payload

class PrefixSerializer:
    def __init__(self, prefix):
        self.prefix = prefix
    def serialize(self, event):
        return f"{self.prefix}{event}"
    def deserialize(self, payload):
        return payload[len(self.prefix):]

def test_subscribe_and_publish():
    eb = EventBus()
    results = []
    eb.subscribe("topic.test", lambda x: results.append(x))
    eb.publish("topic.test", {"foo": "bar"})
    eb.process_queue()
    assert len(results) == 1
    assert '"foo": "bar"' in results[0]

def test_wildcard_subscriptions_single_level():
    eb = EventBus()
    results = []
    eb.subscribe("market.*.nasdaq", lambda x: results.append(x))
    eb.publish("market.us.nasdaq", {"p":1})
    eb.publish("market.eu.nasdaq", {"p":2})
    eb.process_queue()
    assert len(results) == 2

def test_wildcard_subscriptions_multi_level():
    eb = EventBus()
    results = []
    eb.subscribe("market.#", lambda x: results.append(x))
    eb.publish("market", {"p":0})
    eb.publish("market.us.nyse", {"p":3})
    eb.publish("market.eu.frankfurt", {"p":4})
    eb.process_queue()
    assert len(results) == 3

def test_dead_letter_queue():
    eb = EventBus()
    eb.max_retries = 2
    def bad_callback(x):
        raise ValueError("fail")
    eb.subscribe("t.dead", bad_callback)
    eb.publish("t.dead", {"a":1})
    eb.process_queue()
    eb.process_queue()
    eb.process_queue()
    dlq = eb.routeToDeadLetterQueue()
    assert len(dlq) == 1
    assert dlq[0]['topic'] == "t.dead"

def test_encryption():
    eb = EventBus()
    crypto = DummyCrypto()
    eb.registerCryptoModule(crypto)
    results = []
    eb.subscribe("sec.enc", lambda x: results.append(x))
    eb.publish("sec.enc", "secret")
    eb.process_queue()
    # The JSON serializer will wrap the encrypted string in quotes,
    # so we just check that our encryption prefix appears.
    assert 'enc(secret' in results[0]

def test_serializer_registration():
    eb = EventBus()
    eb.registerSerializer("pref", PrefixSerializer(">>"))
    eb.default_serializer = "pref"
    results = []
    eb.subscribe("s.test", lambda x: results.append(x))
    eb.publish("s.test", "data")
    eb.process_queue()
    assert results[0] == ">>data"

def test_backpressure_reject():
    eb = EventBus()
    eb.applyBackpressure(limit=0, policy='reject')
    with pytest.raises(Exception):
        eb.publish("b.r", {"x":1})

def test_backpressure_drop_oldest():
    eb = EventBus()
    eb.applyBackpressure(limit=1, policy='drop_oldest')
    # fill queue without processing
    eb.publish("b.d", 1)
    eb.publish("b.d", 2)
    assert len(eb.event_queue) == 1
    item = eb.event_queue[0]
    assert item['event'] == 2

def test_batch_publish():
    eb = EventBus()
    eb.batchPublish(2)
    results = []
    eb.subscribe("bat.t", lambda x: results.append(x))
    eb.publish("bat.t", "a")
    eb.publish("bat.t", "b")
    eb.process_queue()
    assert len(results) == 1
    assert 'a' in results[0] and 'b' in results[0]

def test_update_config_at_runtime():
    eb = EventBus()
    eb.updateConfigAtRuntime(max_retries=5, queue_limit=10)
    assert eb.max_retries == 5
    assert eb.queue_limit == 10

def test_cluster_deploy():
    eb = EventBus()
    nodes = ["node1", "node2"]
    eb.clusterDeploy(nodes)
    assert eb.cluster_nodes == nodes
    assert eb.leader == "node1"

def test_persist_and_replay():
    eb = EventBus()
    eb.publish("r.p", "x")
    eb.publish("r.p", "y")
    eb.process_queue()
    replay = list(eb.persistAndReplay())
    assert len(replay) == 2
    assert replay[0]['event'] == "x"

def test_register_extension():
    eb = EventBus()
    def ext(payload):
        return payload.upper()
    eb.registerExtension(ext)
    results = []
    eb.subscribe("e.t", lambda x: results.append(x))
    eb.publish("e.t", "ok")
    eb.process_queue()
    assert results[0] == results[0].upper()
