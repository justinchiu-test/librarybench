import pytest
import time
from eventbus import EventBus

def test_propagate_context_and_publishSync():
    bus = EventBus()
    received = {}
    def handler(topic, event):
        received['topic'] = topic
        received['event'] = event
    bus.propagateContext({'device_id':123})
    bus.subscribeWithWildcard('test.topic', handler)
    bus.publishSync('test.topic', {'id':'e1', 'payload': 'data'})
    assert received['topic'] == 'test.topic'
    assert received['event']['id'] == 'e1'
    assert received['event']['payload'] == 'data'
    assert received['event']['ctx'] == {'device_id':123}

def test_subscribeWithWildcard_and_pattern_matching():
    bus = EventBus()
    calls = []
    def handler(topic, event):
        calls.append((topic, event))
    bus.subscribeWithWildcard('device.*.telemetry', handler)
    bus.publishSync('device.001.telemetry', {'id':'e2'})
    bus.publishSync('device.002.telemetry', {'id':'e3'})
    bus.publishSync('device.002.status', {'id':'e4'})
    assert len(calls) == 2
    topics = [c[0] for c in calls]
    assert 'device.001.telemetry' in topics
    assert 'device.002.telemetry' in topics

def test_routeToDeadLetterQueue():
    bus = EventBus()
    bus.propagateContext({'gateway':'gw1'})
    bus.routeToDeadLetterQueue('topic.x', {'id':'e5', 'error':'parse_fail'})
    assert len(bus.dead_letter_queue) == 1
    item = bus.dead_letter_queue[0]
    assert item['topic'] == 'topic.x'
    assert item['event']['id'] == 'e5'
    assert item['event']['error'] == 'parse_fail'
    assert item['event']['ctx'] == {'gateway':'gw1'}

def test_ackEvent():
    bus = EventBus()
    bus.ackEvent('evt123')
    assert 'evt123' in bus.acked_events

def test_setRetryPolicy():
    bus = EventBus()
    policy = {'retries':3, 'intervalMs':1000}
    bus.setRetryPolicy('topic.retry', policy)
    assert bus.retry_policies['topic.retry'] == policy

def test_scheduleDelivery_and_processScheduled():
    bus = EventBus()
    received = []
    def handler(topic, event):
        received.append((topic, event))
    bus.subscribeWithWildcard('sched.topic', handler)
    bus.propagateContext({'ctx':'test'})
    bus.scheduleDelivery('sched.topic', {'id':'e6'}, 0)
    time.sleep(0.01)
    bus.processScheduled()
    assert len(received) == 1
    topic, event = received[0]
    assert topic == 'sched.topic'
    assert event['id'] == 'e6'
    assert event['ctx'] == {'ctx':'test'}

def test_publishBatch():
    bus = EventBus()
    received = []
    def handler(topic, event):
        received.append((topic, event))
    bus.subscribeWithWildcard('batch.topic', handler)
    events = [
        {'topic':'batch.topic', 'event':{'id':'e7'}},
        {'topic':'batch.topic', 'event':{'id':'e8'}},
    ]
    bus.publishBatch(events)
    assert len(received) == 2
    ids = {e[1]['id'] for e in received}
    assert ids == {'e7','e8'}

def test_registerErrorHook_and_error_handling():
    bus = EventBus()
    errors = []
    def handler(topic, event):
        raise ValueError('handler error')
    def error_hook(ex, ctx):
        errors.append((ex, ctx))
    bus.subscribeWithWildcard('err.topic', handler)
    bus.registerErrorHook('global', error_hook)
    bus.propagateContext({'user':'admin'})
    bus.publishSync('err.topic', {'id':'e9'})
    assert len(errors) == 1
    ex, ctx = errors[0]
    assert isinstance(ex, ValueError)
    assert str(ex) == 'handler error'
    assert ctx == {'user':'admin'}

def test_registerPlugin():
    bus = EventBus()
    class DummyPlugin:
        def __init__(self):
            self.called = False
        def setup(self, bus_instance):
            self.called = True
            bus_instance.plugin_registered = True
    plugin = DummyPlugin()
    bus.registerPlugin(plugin)
    assert hasattr(bus, 'plugin_registered')
    assert plugin.called
