import pytest
import time
from event_bus import EventBus

def test_schedule_delivery():
    bus = EventBus()
    event = {'id': 'e1', 'data': 'test'}
    bus.scheduleDelivery('order.abandonedCartReminder', event, 100)
    assert len(bus.scheduled) == 1
    due, topic, ev = bus.scheduled[0]
    assert topic == 'order.abandonedCartReminder'
    assert ev == event
    assert due >= int(time.time() * 1000)

def test_subscribe_wildcard_star():
    bus = EventBus()
    received = []
    def handler(e):
        received.append(e)
    bus.subscribeWithWildcard('order.*', handler)
    bus.publishSync('order.created', {'id': 'e2'})
    bus.publishSync('order.updated', {'id': 'e3'})
    bus.publishSync('inventory.updated', {'id': 'e4'})
    assert len(received) == 2
    ids = [e['id'] for e in received]
    assert 'e2' in ids and 'e3' in ids

def test_subscribe_wildcard_hash():
    bus = EventBus()
    received = []
    def handler(e):
        received.append(e)
    bus.subscribeWithWildcard('inventory.#', handler)
    bus.publishSync('inventory', {'id': 'i1'})
    bus.publishSync('inventory.stock', {'id': 'i2'})
    bus.publishSync('inventory.stock.update', {'id': 'i3'})
    bus.publishSync('order.inventory', {'id': 'i4'})
    assert [e['id'] for e in received] == ['i1', 'i2', 'i3']

def test_subscribe_wildcard_set():
    bus = EventBus()
    received = []
    def handler(e):
        received.append(e)
    bus.subscribeWithWildcard('user.{login,profile}', handler)
    bus.publishSync('user.login', {'id': 'u1'})
    bus.publishSync('user.profile', {'id': 'u2'})
    bus.publishSync('user.logout', {'id': 'u3'})
    assert [e['id'] for e in received] == ['u1', 'u2']

def test_ack_event():
    bus = EventBus()
    ev = {'id': 'a1'}
    bus.subscribeWithWildcard('test', lambda e: None)
    bus.publishSync('test', ev)
    assert 'a1' in bus.in_flight
    bus.ackEvent('a1')
    assert 'a1' not in bus.in_flight

def test_error_hook_on_exception():
    bus = EventBus()
    ev = {'id': 'err1'}
    errors = []
    def bad_handler(e):
        raise ValueError("fail")
    def hook(topic, event, error):
        errors.append((topic, event, type(error)))
    bus.subscribeWithWildcard('fail.test', bad_handler)
    bus.registerErrorHook('global', hook)
    bus.publishSync('fail.test', ev)
    assert len(errors) == 1
    topic, event, err_type = errors[0]
    assert topic == 'fail.test'
    assert event == ev
    assert err_type is ValueError

def test_route_to_dlq_after_retries():
    bus = EventBus()
    ev = {'id': 'd1'}
    calls = []
    def bad(e):
        calls.append(1)
        raise RuntimeError("bad")
    bus.subscribeWithWildcard('paymentConfirmed', bad)
    bus.setRetryPolicy('paymentConfirmed', {'max_retries': 2})
    bus.publish('paymentConfirmed', ev)
    # should have been called 3 times: initial + 2 retries
    assert len(calls) == 3
    # dead letter queue should contain the event
    assert bus.dead_letter_queue == [('paymentConfirmed', ev)]

def test_publish_batch_and_context():
    bus = EventBus()
    received = []
    def handler(e):
        received.append((e['id'], e.get('ctx')))
    bus.subscribeWithWildcard('batch.topic', handler)
    bus.propagateContext({'session': 's1'})
    events = [('batch.topic', {'id': 'b1'}), ('batch.topic', {'id': 'b2'})]
    bus.publishBatch(events)
    assert len(received) == 2
    assert received[0] == ('b1', {'session': 's1'})
    assert received[1] == ('b2', {'session': 's1'})

def test_register_plugin():
    bus = EventBus()
    calls = []
    class Plugin:
        def pre_publish(self, topic, event):
            calls.append(('pre', topic, event.get('id')))
        def post_publish(self, topic, event):
            calls.append(('post', topic, event.get('id')))
    plugin = Plugin()
    bus.registerPlugin(plugin)
    bus.subscribeWithWildcard('plug.topic', lambda e: None)
    bus.publishSync('plug.topic', {'id': 'p1'})
    assert ('pre', 'plug.topic', 'p1') in calls
    assert ('post', 'plug.topic', 'p1') in calls
