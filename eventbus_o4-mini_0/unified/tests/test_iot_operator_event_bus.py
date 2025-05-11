import os
import shutil
import threading
import time
import pytest
from iot_operator.iot_event_bus import EventBus, JsonSerializer, Serializer

class DummyCrypto:
    def __init__(self, key=0x01):
        self.key = key
    def encrypt(self, data: bytes) -> bytes:
        return bytes(b ^ self.key for b in data)
    def decrypt(self, data: bytes) -> bytes:
        return bytes(b ^ self.key for b in data)

class DummyBadCrypto:
    def encrypt(self, data: bytes) -> bytes:
        return data
    def decrypt(self, data: bytes) -> bytes:
        raise ValueError("Corrupt")

def test_subscribe_and_publish():
    bus = EventBus()
    results = []
    bus.subscribeWildcard('site/*/temp', lambda t, m: results.append((t, m)))
    bus.publish('site/room1/temp', {'val': 22})
    assert results == [('site/room1/temp', {'val': 22})]

def test_multi_level_wildcard():
    bus = EventBus()
    results = []
    bus.subscribeWildcard('site/#', lambda t, m: results.append((t, m)))
    bus.publish('site/a/b/c', 'hello')
    assert results == [('site/a/b/c', 'hello')]

def test_dead_letter_on_exception_in_callback():
    bus = EventBus()
    def bad_cb(t, m):
        raise RuntimeError("error")
    bus.subscribeWildcard('foo', bad_cb)
    bus.publish('foo', 'x')
    dlq = bus.getDeadLetterQueue()
    assert dlq and dlq[0][0] == 'foo'

def test_encryption_and_decryption():
    bus = EventBus()
    crypto = DummyCrypto()
    bus.encryptEvent(crypto)
    results = []
    bus.subscribeWildcard('enc/test', lambda t, m: results.append(m))
    bus.publish('enc/test', {'data': 123})
    assert results == [{'data': 123}]

def test_dead_letter_on_decrypt_failure():
    bus = EventBus()
    bus.encryptEvent(DummyBadCrypto())
    bus.subscribeWildcard('x', lambda t, m: None)
    bus.publish('x', {'a':1})
    dlq = bus.getDeadLetterQueue()
    assert dlq

def test_backpressure_reject():
    bus = EventBus()
    bus.applyBackpressure('reject', queue_limit=1)
    bus.subscribeWildcard('t', lambda t, m: None)
    bus.publish('t', {'a':1})
    with pytest.raises(RuntimeError):
        bus.publish('t', {'a':2})

def test_backpressure_drop_oldest():
    bus = EventBus()
    bus.applyBackpressure('drop_oldest', queue_limit=1)
    results = []
    bus.subscribeWildcard('t', lambda t, m: results.append(m))
    bus.publish('t', {'a':1})
    bus.publish('t', {'a':2})
    assert results == [{'a':2}]

def test_register_serializer_and_usage():
    bus = EventBus()
    class UppercaseSerializer(Serializer):
        def dumps(self, obj):
            return str(obj).upper().encode('utf-8')
        def loads(self, data):
            return data.decode('utf-8').lower()
    bus.registerSerializer('up', UppercaseSerializer())
    results = []
    bus.subscribeWildcard('u', lambda t, m: results.append(m))
    bus.publish('u', 'test', serializer='up')
    assert results == ['test']

def test_batch_publish():
    bus = EventBus()
    results = []
    bus.subscribeWildcard('batch', lambda t, m: results.append(m))
    bus.batchPublish('batch', [1,2,3])
    assert results == [1,2,3]

def test_update_config_at_runtime():
    bus = EventBus()
    bus.updateConfigAtRuntime({'queue_limit':2, 'backpressure_policy':'reject'})
    assert bus._queue_limit == 2
    assert bus._backpressure_policy == 'reject'

def test_cluster_deploy_flag():
    bus = EventBus()
    bus.clusterDeploy()
    assert bus._cluster_deployed

def test_persist_and_replay(tmp_path):
    bus = EventBus()
    # override persist dir
    bus._persist_dir = str(tmp_path)
    msg = {'x':1}
    bus.persistAndReplay('t', msg)
    events = bus.persistAndReplay(None)
    assert any(e['message']==msg for e in events)

def test_register_extension():
    bus = EventBus()
    called = []
    def ext(topic, msg):
        called.append((topic, msg))
    bus.registerExtension(ext)
    bus.subscribeWildcard('e', lambda t, m: None)
    bus.publish('e', 42)
    assert called == [('e', 42)]
