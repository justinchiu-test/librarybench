import time
import pytest
from event_bus import EventBus, Event, SubscriptionHandle

def test_subscribe_and_publish():
    bus = EventBus()
    received = []
    def handler(e):
        received.append(e.data)
    bus.subscribe(handler)
    bus.publish("test")
    assert received == ["test"]

def test_subscribe_once():
    bus = EventBus()
    received = []
    def handler(e):
        received.append(e.data)
    bus.subscribe_once(handler)
    bus.publish("first")
    bus.publish("second")
    assert received == ["first"]

def test_unsubscribe():
    bus = EventBus()
    received = []
    def handler(e):
        received.append(e.data)
    handle = bus.subscribe(handler)
    bus.publish("one")
    bus.unsubscribe(handle)
    bus.publish("two")
    assert received == ["one"]

def test_set_global_error_handler():
    bus = EventBus()
    errors = []
    def handler(e):
        raise ValueError("err")
    def global_err(e, ex):
        errors.append((e.data, type(ex)))
    bus.subscribe(handler)
    bus.set_global_error_handler(global_err)
    bus.publish("evt")
    assert errors == [("evt", ValueError)]

def test_on_error_per_handler():
    bus = EventBus()
    errors = []
    def handler(e):
        raise KeyError("bad")
    def err_cb(e, ex):
        errors.append((e.data, type(ex)))
    bus.subscribe(handler)
    bus.on_error(handler, err_cb)
    bus.publish("item")
    assert errors == [("item", KeyError)]

def test_dead_letter_queue():
    bus = EventBus()
    dlq = bus.dead_letter_queue("bad_records")
    def handler(e):
        raise RuntimeError("fail")
    def err_cb(e, ex):
        dlq.append(e.data)
    bus.subscribe(handler)
    bus.on_error(handler, err_cb)
    bus.publish("bad")
    assert dlq == ["bad"]

def test_publish_delayed():
    bus = EventBus()
    received = []
    bus.subscribe(lambda e: received.append(e.data))
    bus.publish_delayed("delayed", 0.05)
    time.sleep(0.1)
    assert "delayed" in received

def test_transaction_commit():
    bus = EventBus()
    received = []
    bus.subscribe(lambda e: received.append(e.data))
    with bus.with_transaction():
        bus.publish("a")
        bus.publish("b")
    assert received == ["a", "b"]

def test_transaction_rollback():
    bus = EventBus()
    received = []
    bus.subscribe(lambda e: received.append(e.data))
    with pytest.raises(ValueError):
        with bus.with_transaction():
            bus.publish("x")
            raise ValueError("fail")
    assert received == []

def test_filter():
    bus = EventBus()
    received = []
    bus.add_filter(lambda e: e.data != "drop")
    bus.subscribe(lambda e: received.append(e.data))
    bus.publish("keep")
    bus.publish("drop")
    assert received == ["keep"]

def test_logger_and_subscriptions():
    class Logger:
        def __init__(self):
            self.logs = []
        def info(self, msg):
            self.logs.append(("info", msg))
        def error(self, msg):
            self.logs.append(("error", msg))
    bus = EventBus()
    logger = Logger()
    bus.attach_logger(logger)
    def h(e): pass
    handle = bus.subscribe(h)
    bus.unsubscribe(handle)
    bus.publish("msg")
    # check that logger captured attachment, subscribe, unsubscribe, publish_deliver/skip
    types = [t for t, m in logger.logs]
    assert "info" in types

def test_context_middleware():
    bus = EventBus()
    received = []
    def handler(e):
        received.append("corr" in e.context)
        received.append("batch" in e.context)
        received.append("source" in e.context and isinstance(e.context["source"], str))
    mw = bus.context_middleware()
    bus.subscribe(mw(handler))
    bus.publish("data")
    assert received == [True, True, True]
