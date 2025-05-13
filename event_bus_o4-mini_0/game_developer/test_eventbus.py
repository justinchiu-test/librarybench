import pytest
import time
from eventbus import EventBus

class DummyLogger:
    def __init__(self):
        self.published = []
        self.delivered = []
        self.subscribed = []
        self.unsubscribed = []
        self.errors = []

    def log_publish(self, event):
        self.published.append(event)

    def log_delivery(self, handler, event):
        self.delivered.append((handler, event))

    def log_subscribe(self, handle, handler, once=False):
        self.subscribed.append((handle, handler, once))

    def log_unsubscribe(self, handle, handler):
        self.unsubscribed.append((handle, handler))

    def log_error(self, handler, event, error):
        self.errors.append((handler, event, error))

def test_subscribe_and_publish():
    bus = EventBus()
    results = []
    def handler(e):
        results.append(e['payload'])
    bus.subscribe(handler)
    bus.publish('player_moved', 1)
    assert results == [1]

def test_subscribe_once():
    bus = EventBus()
    results = []
    def handler(e):
        results.append(e['payload'])
    bus.subscribe_once(handler)
    bus.publish('tutorial_complete', 2)
    bus.publish('tutorial_complete', 3)
    assert results == [2]

def test_unsubscribe():
    bus = EventBus()
    results = []
    def handler(e):
        results.append(e)
    h = bus.subscribe(handler)
    bus.publish('x', None)
    bus.unsubscribe(h)
    bus.publish('x', None)
    assert len(results) == 1

def test_global_error_handler():
    bus = EventBus()
    errors = []
    def global_err(e, err):
        errors.append((e['type'], str(err)))
    bus.set_global_error_handler(global_err)
    def bad(e):
        raise ValueError("oops")
    bus.subscribe(bad)
    bus.publish('shot_fired', None)
    assert errors and errors[0][0] == 'shot_fired'

def test_on_error_specific():
    bus = EventBus()
    results = []
    def bad(e):
        raise RuntimeError("bad")
    def cb(e, err):
        results.append(str(err))
    bus.subscribe(bad)
    bus.on_error(bad, cb)
    bus.publish('x', None)
    assert results and "bad" in results[0]

def test_dead_letter_queue():
    bus = EventBus()
    dl = []
    bus.dead_letter_queue("game_dead")
    def bad(e):
        raise Exception("fail")
    def dlq_handler(e):
        dl.append(e['payload']['original']['type'])
    bus.subscribe(bad)
    bus.subscribe(dlq_handler)
    bus.publish('powerup_spawned', None)
    # allow nested publication
    time.sleep(0.01)
    assert 'powerup_spawned' in dl

def test_publish_delayed():
    bus = EventBus()
    results = []
    bus.subscribe(lambda e: results.append(e['payload']))
    bus.publish_delayed('x', 42, 0.05)
    time.sleep(0.1)
    assert results == [42]

def test_transaction_success_commit():
    bus = EventBus()
    results = []
    bus.subscribe(lambda e: results.append(e['payload']))
    with bus.with_transaction():
        bus.publish('a', 1)
        bus.publish('b', 2)
    assert results == [1, 2]

def test_transaction_rollback():
    bus = EventBus()
    results = []
    bus.subscribe(lambda e: results.append(e['payload']))
    with pytest.raises(ValueError):
        with bus.with_transaction():
            bus.publish('a', 1)
            raise ValueError("fail")
    # aborted, should not have delivered
    assert results == []

def test_filtering():
    bus = EventBus()
    results = []
    bus.add_filter(lambda e: e['payload'] % 2 == 0)
    bus.subscribe(lambda e: results.append(e['payload']))
    bus.publish('x', 1)
    bus.publish('x', 2)
    assert results == [2]

def test_logger_integration():
    bus = EventBus()
    logger = DummyLogger()
    bus.attach_logger(logger)
    h = bus.subscribe(lambda e: None)
    bus.unsubscribe(h)
    bus.publish('x', 5)
    assert logger.published and logger.subscribed and logger.unsubscribed

def test_context_middleware():
    bus = EventBus()
    results = []
    def handler(e):
        results.append(e['context'])
    bus.subscribe(handler)
    with bus.context_middleware(session_id='s1', match_id='m1'):
        bus.publish('x', None)
    assert results == [{'session_id': 's1', 'match_id': 'm1'}]
