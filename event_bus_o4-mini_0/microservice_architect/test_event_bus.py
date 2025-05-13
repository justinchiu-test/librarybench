import threading
import time
import pytest
from event_bus import EventBus

def test_subscribe_and_publish():
    bus = EventBus()
    results = []
    def handler(evt):
        results.append(evt)
    bus.subscribe(handler)
    bus.publish("hello")
    assert results == ["hello"]

def test_subscribe_once():
    bus = EventBus()
    results = []
    def handler(evt):
        results.append(evt)
    bus.subscribe_once(handler)
    bus.publish(1)
    bus.publish(2)
    assert results == [1]

def test_unsubscribe():
    bus = EventBus()
    results = []
    def handler(evt):
        results.append(evt)
    h = bus.subscribe(handler)
    bus.publish("a")
    bus.unsubscribe(h)
    bus.publish("b")
    assert results == ["a"]

def test_global_error_handler():
    bus = EventBus()
    caught = []
    def global_err(e, evt):
        caught.append((e, evt))
    bus.set_global_error_handler(global_err)
    def bad(evt):
        raise ValueError("oops")
    bus.subscribe(bad)
    bus.publish("x")
    assert len(caught) == 1
    exc, evt = caught[0]
    assert isinstance(exc, ValueError)
    assert evt == "x"

def test_on_error_per_subscriber():
    bus = EventBus()
    caught = []
    def bad(evt):
        raise RuntimeError("fail")
    def err_cb(e, evt):
        caught.append((e, evt))
    h = bus.subscribe(bad)
    bus.on_error(bad, err_cb)
    bus.publish("y")
    assert len(caught) == 1
    exc, evt = caught[0]
    assert isinstance(exc, RuntimeError)
    assert evt == "y"

def test_dead_letter_queue():
    bus = EventBus()
    dlq = bus.dead_letter_queue("dlq")
    def bad(evt):
        raise KeyError("kludge")
    bus.subscribe(bad)
    bus.publish("evt")
    assert len(dlq) == 1
    evt, exc = dlq[0]
    assert evt == "evt"
    assert isinstance(exc, KeyError)

def test_publish_delayed():
    bus = EventBus()
    results = []
    def handler(evt):
        results.append(evt)
    bus.subscribe(handler)
    bus.publish_delayed("delayed", 0.1)
    time.sleep(0.2)
    assert results == ["delayed"]

def test_with_transaction_commit():
    bus = EventBus()
    results = []
    def handler(evt):
        results.append(evt)
    bus.subscribe(handler)
    with bus.with_transaction():
        bus.publish(1)
        bus.publish(2)
    assert results == [1, 2]

def test_with_transaction_rollback():
    bus = EventBus()
    results = []
    def handler(evt):
        results.append(evt)
    bus.subscribe(handler)
    with pytest.raises(ValueError):
        with bus.with_transaction():
            bus.publish("ok")
            raise ValueError("fail")
            bus.publish("ignored")
    assert results == []

def test_add_filter():
    bus = EventBus()
    results = []
    def handler(evt):
        results.append(evt)
    bus.subscribe(handler)
    bus.add_filter(lambda e: isinstance(e, int))
    bus.publish(1)
    bus.publish("bad")
    assert results == [1]

def test_logger_hooks():
    bus = EventBus()
    calls = []
    class Logger:
        def on_subscribe(self, h): calls.append(("sub", h))
        def on_unsubscribe(self, h): calls.append(("unsub", h))
        def on_publish(self, evt): calls.append(("pub", evt))
        def on_deliver(self, h, evt): calls.append(("deliv", h, evt))
        def on_error(self, h, evt, e): calls.append(("err", h, evt, type(e)))
        def on_filter_drop(self, evt): calls.append(("drop", evt))
    logger = Logger()
    bus.attach_logger(logger)
    # subscribe
    def good(evt): pass
    h1 = bus.subscribe(good)
    # publish
    bus.publish("a")
    # filter
    bus.add_filter(lambda e: False)
    bus.publish("b")
    # error path
    def bad(evt): raise ZeroDivisionError()
    h2 = bus.subscribe(bad)
    bus.publish("c")
    # unsubscribe
    bus.unsubscribe(h1)
    # check sequence
    types = [c[0] for c in calls]
    expected = [
        "sub",        # subscribe good
        "pub",        # publish a
        "deliv",      # deliver good,a
        "drop",       # drop b
        "sub",        # subscribe bad
        "pub",        # publish c
        "err",        # error bad,c
        "unsub"       # unsubscribe good
    ]
    assert types == expected

def test_context_middleware():
    bus = EventBus()
    results = []
    def handler(evt):
        rid = bus.get_context("request_id")
        results.append((evt, rid))
    bus.context_middleware()
    bus.set_context("request_id", "abc-123")
    bus.subscribe(handler)
    bus.publish("ctx")
    assert results == [("ctx", "abc-123")]
