import pytest
import time
from eventbus import EventBus

def test_publish_and_subscribe():
    bus = EventBus()
    results = []
    def handler(event, ctx):
        results.append((event, ctx))
    bus.subscribeWithWildcard('foo', handler)
    ctx = {'req_id': '123'}
    eid = bus.publishSync('foo', {'data':1}, ctx)
    assert results == [({'data':1}, ctx)]
    assert isinstance(eid, int)

def test_wildcard_subscription_star():
    bus = EventBus()
    results = []
    def handler(event, ctx):
        results.append(event)
    bus.subscribeWithWildcard('metrics.*', handler)
    bus.publishSync('metrics.cpu', 1)
    bus.publishSync('metrics.mem', 2)
    bus.publishSync('metric.cpu', 3)
    assert results == [1, 2]

def test_wildcard_subscription_brace():
    bus = EventBus()
    results = []
    def handler(event, ctx):
        results.append(event)
    bus.subscribeWithWildcard('sensor.{temp,pressure}', handler)
    bus.publishSync('sensor.temp', 't')
    bus.publishSync('sensor.pressure', 'p')
    bus.publishSync('sensor.humidity', 'h')
    assert results == ['t', 'p']

def test_schedule_delivery():
    bus = EventBus()
    results = []
    def handler(event, ctx):
        results.append(event)
    bus.subscribeWithWildcard('delayed', handler)
    bus.scheduleDelivery('delayed', 'hello', 50)
    time.sleep(0.1)
    assert results == ['hello']

def test_ackEvent_stops_retries():
    bus = EventBus()
    calls = []
    def handler(event, ctx):
        calls.append(1)
        raise ValueError()
    bus.subscribeWithWildcard('fail', handler)
    bus.setRetryPolicy('fail', {'maxRetries':5, 'initialDelay':10, 'backoffType':'fixed'})
    eid = bus.publishSync('fail', 'e1')
    bus.ackEvent(eid)
    time.sleep(0.05)
    assert len(calls) == 1
    assert bus.dead_letter_queue == []

def test_dead_letter_queue_after_retries():
    bus = EventBus()
    calls = []
    def handler(event, ctx):
        calls.append(1)
        raise RuntimeError()
    bus.subscribeWithWildcard('topic1', handler)
    bus.setRetryPolicy('topic1', {'maxRetries':2, 'initialDelay':10, 'backoffType':'fixed'})
    bus.publishSync('topic1', 'e2')
    time.sleep(0.1)
    assert len(calls) == 3  # 1 initial + 2 retries
    assert bus.dead_letter_queue == [('topic1', 'e2')]

def test_error_hooks():
    bus = EventBus()
    errors = []
    def hook(topic, event, exc):
        errors.append((topic, event, type(exc)))
    def handler(event, ctx):
        raise KeyError()
    bus.registerErrorHook('global', hook)
    bus.registerErrorHook('topic1', hook)
    bus.subscribeWithWildcard('topic1', handler)
    bus.publishSync('topic1', 'e3')
    time.sleep(0.05)
    assert errors.count(('topic1', 'e3', KeyError)) == 2

def test_publish_batch_and_order():
    bus = EventBus()
    results = []
    def handler(event, ctx):
        results.append(event)
    bus.subscribeWithWildcard('batch', handler)
    events = [('batch', 'a'), ('batch', 'b'), ('batch', 'c')]
    bus.publishBatch(events)
    assert results == ['a', 'b', 'c']

def test_propagate_context():
    bus = EventBus()
    results = []
    def handler(event, ctx):
        results.append(ctx.get('trace'))
    bus.subscribeWithWildcard('ctx', handler)
    bus.publishSync('ctx', 'e', {'trace': 'xyz'})
    assert results == ['xyz']

def test_set_retry_policy_storage():
    bus = EventBus()
    policy = {'maxRetries':3, 'initialDelay':100, 'backoffType':'exponential'}
    bus.setRetryPolicy('topicX', policy)
    assert bus.retry_policies['topicX'] == policy

def test_register_plugin():
    bus = EventBus()
    called = []
    class Plugin:
        def register(self, b):
            called.append(b)
    p = Plugin()
    bus.registerPlugin(p)
    assert p in bus.plugins
    assert called == [bus]
