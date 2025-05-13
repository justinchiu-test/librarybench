import time
import threading
import pytest
from event_bus import EventBus

def test_schedule_delivery():
    bus = EventBus()
    results = []
    def handler(e):
        results.append(e['id'])
    bus.subscribeWithWildcard('topic1', handler)
    bus.scheduleDelivery('topic1', {'id': 1}, 100)
    time.sleep(0.2)
    assert results == [1]

def test_route_to_dead_letter_queue():
    bus = EventBus()
    event = {'id': 'e1'}
    bus.routeToDeadLetterQueue('t', event)
    assert ('t', event) in bus.dlq

def test_subscribe_with_wildcard_star():
    bus = EventBus()
    results = []
    def handler(e):
        results.append(e['id'])
    bus.subscribeWithWildcard('service.*.events', handler)
    bus.publishSync('service.order.events', {'id': 1})
    bus.publishSync('service.payment.events', {'id': 2})
    bus.publishSync('service.order.processed', {'id': 3})
    assert results == [1, 2]

def test_subscribe_with_wildcard_hash():
    bus = EventBus()
    results = []
    def handler(e):
        results.append(e['id'])
    bus.subscribeWithWildcard('workflow.#', handler)
    bus.publishSync('workflow.start', {'id': 1})
    bus.publishSync('workflow.step.1', {'id': 2})
    bus.publishSync('other.workflow', {'id': 3})
    assert results == [1, 2]

def test_ack_event():
    bus = EventBus()
    bus.ackEvent('eid')
    assert 'eid' in bus.acked

def test_register_error_hook_and_publish_error():
    bus = EventBus()
    calls = []
    def bad_handler(e):
        raise ValueError("fail")
    def global_hook(scope, err, topic, event):
        calls.append(('g', scope, str(err)))
    def topic_hook(scope, err, topic, event):
        calls.append(('t', scope, str(err)))
    bus.subscribeWithWildcard('e', bad_handler)
    bus.registerErrorHook('global', global_hook)
    bus.registerErrorHook('e', topic_hook)
    bus.publishSync('e', {'id': 'x'})
    # allow any retries to schedule (none by default)
    time.sleep(0.05)
    # both hooks should have been called once
    assert ('g', 'global', 'fail') in calls
    assert ('t', 'e', 'fail') in calls

def test_publish_sync():
    bus = EventBus()
    results = []
    def handler(e):
        results.append(e['id'])
    bus.subscribeWithWildcard('t1', handler)
    bus.publishSync('t1', {'id': 10})
    assert results == [10]

def test_publish_batch():
    bus = EventBus()
    results = []
    def h1(e):
        results.append(('h1', e['id']))
    def h2(e):
        results.append(('h2', e['id']))
    bus.subscribeWithWildcard('a', h1)
    bus.subscribeWithWildcard('b', h2)
    events = [
        ('a', {'id': 1}),
        {'topic': 'b', 'event': {'id': 2}}
    ]
    bus.publishBatch(events)
    assert ('h1', 1) in results
    assert ('h2', 2) in results

def test_propagate_context():
    bus = EventBus()
    results = []
    def handler(e):
        results.append(e.get('context'))
    bus.propagateContext({'foo': 'bar'})
    bus.subscribeWithWildcard('ctx', handler)
    bus.publishSync('ctx', {'id': 1})
    assert results == [{'foo': 'bar'}]

def test_set_retry_policy_fixed():
    bus = EventBus()
    calls = []
    lock = threading.Lock()
    def flaky(e):
        with lock:
            calls.append(time.time())
            if len(calls) < 3:
                raise RuntimeError("retry")
    bus.subscribeWithWildcard('r', flaky)
    bus.setRetryPolicy('r', {'type': 'fixed', 'retries': 2, 'delayMs': 50})
    bus.publishSync('r', {'id': 5})
    time.sleep(0.3)
    assert len(calls) == 3
    assert bus.dlq == []

def test_set_retry_policy_exponential():
    bus = EventBus()
    calls = []
    lock = threading.Lock()
    def flaky(e):
        with lock:
            calls.append(time.time())
            if len(calls) < 3:
                raise RuntimeError("retry")
    bus.subscribeWithWildcard('rx', flaky)
    bus.setRetryPolicy('rx', {'type': 'exponential', 'retries': 2, 'initialDelayMs': 10})
    bus.publishSync('rx', {'id': 6})
    time.sleep(0.2)
    assert len(calls) == 3
    assert bus.dlq == []

def test_register_plugin():
    bus = EventBus()
    class Plugin:
        def __init__(self):
            self.called = False
        def onPublish(self, topic, event):
            self.called = True
    plugin = Plugin()
    bus.registerPlugin(plugin)
    def handler(e):
        pass
    bus.subscribeWithWildcard('p', handler)
    bus.publishSync('p', {'id': 7})
    assert plugin.called
