import threading
import time
import pytest
import event_bus
from event_bus import (
    subscribeWithWildcard, publishSync, publishBatch, propagateContext,
    setRetryPolicy, registerErrorHook, routeToDeadLetterQueue,
    ackEvent, scheduleDelivery, registerPlugin, default_bus, resetBus
)

def setup_function():
    resetBus()

def test_subscribe_and_publish_sync():
    called = []
    def handler(topic, event, context):
        called.append((topic, event, context))
    subscribeWithWildcard('game.start', handler)
    propagateContext({'user': 1})
    publishSync('game.start', {'foo': 'bar'})
    assert called == [('game.start', {'foo': 'bar'}, {'user': 1})]

def test_wildcard_star_matching():
    called = []
    def handler(t, e, c):
        called.append((t, e))
    subscribeWithWildcard('player.*.move', handler)
    publishSync('player.123.move', {'x': 10})
    publishSync('player.abc.move', {'y': 20})
    publishSync('player.1.attack', {'z': 30})
    assert ('player.123.move', {'x': 10}) in called
    assert ('player.abc.move', {'y': 20}) in called
    assert all(t.endswith('.move') for t, _ in called)

def test_wildcard_hash_matching():
    called = []
    def handler(t, e, c):
        called.append(t)
    subscribeWithWildcard('zone.#.update', handler)
    publishSync('zone.update', {})
    publishSync('zone.a.update', {})
    publishSync('zone.a.b.c.update', {})
    publishSync('zone.a.b.delete', {})
    assert 'zone.update' in called
    assert 'zone.a.update' in called
    assert 'zone.a.b.c.update' in called
    assert all(t.endswith('.update') for t in called)

def test_schedule_delivery():
    called = []
    evt = threading.Event()
    def handler(t, e, c):
        called.append((t, e))
        evt.set()
    subscribeWithWildcard('boss.spawn', handler)
    scheduleDelivery('boss.spawn', {'hp': 100}, 100)
    evt.wait(1)
    assert called == [('boss.spawn', {'hp': 100})]

def test_route_to_dead_letter_queue():
    routeToDeadLetterQueue('topic1', {'bad': True})
    assert ('topic1', {'bad': True}) in default_bus.dead_letter_queue

def test_ack_event():
    ackEvent('evt1')
    assert 'evt1' in default_bus.acked_events

def test_error_hooks():
    errors = []
    def bad_handler(t, e, c):
        raise ValueError("fail")
    def global_hook(exc, t, e):
        errors.append(('global', type(exc), t))
    def specific_hook(exc, t, e):
        errors.append(('specific', type(exc), t))
    registerErrorHook('global', global_hook)
    subscribeWithWildcard('test.error', bad_handler)
    registerErrorHook('test.error', specific_hook)
    publishSync('test.error', {'data': 1})
    assert ('specific', ValueError, 'test.error') in errors
    assert ('global', ValueError, 'test.error') in errors
    # after failure, routed to dead letter
    assert ('test.error', {'data': 1}) in default_bus.dead_letter_queue

def test_retry_policy_success():
    calls = {'count': 0}
    def flaky(t, e, c):
        calls['count'] += 1
        if calls['count'] < 3:
            raise RuntimeError("try again")
    subscribeWithWildcard('retry.topic', flaky)
    setRetryPolicy('retry.topic', {'retries': 2, 'delayMs': 0})
    publishSync('retry.topic', {'ok': True})
    assert calls['count'] == 3
    assert ('retry.topic', {'ok': True}) not in default_bus.dead_letter_queue

def test_retry_policy_exhaust():
    calls = {'count': 0}
    def always_fail(t, e, c):
        calls['count'] += 1
        raise RuntimeError("oops")
    subscribeWithWildcard('fail.topic', always_fail)
    setRetryPolicy('fail.topic', {'retries': 1, 'delayMs': 0})
    publishSync('fail.topic', {'bad': True})
    assert calls['count'] == 2
    assert ('fail.topic', {'bad': True}) in default_bus.dead_letter_queue

def test_publish_batch():
    called = []
    def h1(t, e, c):
        called.append(('h1', t, e))
    def h2(t, e, c):
        called.append(('h2', t, e))
    subscribeWithWildcard('a.one', h1)
    subscribeWithWildcard('b.two', h2)
    batch = [
        {'topic': 'a.one', 'event': {'v': 1}},
        {'topic': 'b.two', 'event': {'v': 2}},
    ]
    publishBatch(batch)
    assert ('h1', 'a.one', {'v': 1}) in called
    assert ('h2', 'b.two', {'v': 2}) in called

def test_propagate_context():
    called = []
    def handler(t, e, c):
        called.append(c)
    subscribeWithWildcard('ctx.test', handler)
    propagateContext({'session': 'xyz'})
    publishSync('ctx.test', {})
    assert called == [{'session': 'xyz'}]

def test_register_plugin():
    class Plugin:
        def __init__(self):
            self.initialized = False
        def init(self, bus):
            self.initialized = True
            self.bus_ref = bus
    plugin = Plugin()
    registerPlugin(plugin)
    assert plugin in default_bus.plugins
    assert plugin.initialized is True
    assert plugin.bus_ref is default_bus
