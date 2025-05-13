import time
import pytest
from iot_bus import EventBus, bus

def test_subscribe_and_publish():
    bus = EventBus()
    received = []
    def handler(e):
        received.append(e)
    bus.subscribe(handler)
    event = {'sensor_type': 'temp', 'value': 42}
    bus.publish(event)
    assert received == [event]

def test_subscribe_once():
    bus = EventBus()
    count = []
    def handler(e):
        count.append(e)
    bus.subscribe_once(handler)
    bus.publish({'a': 1})
    bus.publish({'a': 2})
    assert len(count) == 1

def test_unsubscribe():
    bus = EventBus()
    received = []
    def handler(e):
        received.append(e)
    sub_id = bus.subscribe(handler)
    bus.unsubscribe(sub_id)
    bus.publish({'x': 'y'})
    assert received == []

def test_set_global_error_handler_and_dlq():
    bus = EventBus()
    bus.dead_letter_queue("quarantine")
    caught = []
    def global_err(exc, event):
        caught.append((exc, event))
    bus.set_global_error_handler(global_err)
    def handler(e):
        raise ValueError("oops")
    bus.subscribe(handler)
    ev = {'k': 'v'}
    bus.publish(ev)
    assert len(caught) == 1
    exc, event = caught[0]
    assert isinstance(exc, ValueError) and event == ev
    # dead letter should have stored tuple
    dl = bus.dead_letters["quarantine"]
    assert dl and dl[0][0] == ev and isinstance(dl[0][1], ValueError)

def test_on_error_callback():
    bus = EventBus()
    received = []
    def handler(e):
        raise RuntimeError("fail")
    def err_cb(event, exc):
        received.append((event, exc))
    bus.subscribe(handler)
    bus.on_error(handler, err_cb)
    bus.dead_letter_queue("quarantine")
    ev = {'k': 'v2'}
    bus.publish(ev)
    assert len(received) == 1
    assert received[0][0] == ev and isinstance(received[0][1], RuntimeError)

def test_publish_delayed():
    bus = EventBus()
    received = []
    def handler(e):
        received.append(e)
    bus.subscribe(handler)
    ev = {'d': 123}
    bus.publish_delayed(ev, 0.1)
    time.sleep(0.2)
    assert received == [ev]

def test_transaction_commit_and_abort():
    bus = EventBus()
    rec = []
    def handler(e):
        rec.append(e)
    bus.subscribe(handler)
    # commit case
    with bus.with_transaction():
        bus.publish({'tx': 1})
        bus.publish_delayed({'txd': 2}, 0.05)
    # after exit, buffered publish appears
    assert {'tx': 1} in rec
    # delayed should also fire
    time.sleep(0.1)
    assert {'txd': 2} in rec
    # abort case
    rec.clear()
    try:
        with bus.with_transaction():
            bus.publish({'(tx)': 'A'})
            raise Exception("fail tx")
    except:
        pass
    # nothing should be published
    assert rec == []

def test_filters():
    bus = EventBus()
    rec = []
    def handler(e):
        rec.append(e)
    bus.subscribe(handler)
    bus.add_filter(lambda e: e.get('sensor_type') == 'temperature')
    bus.publish({'sensor_type': 'gps'})
    bus.publish({'sensor_type': 'temperature', 'value': 5})
    assert rec == [{'sensor_type': 'temperature', 'value': 5}]

def test_context_middleware():
    bus = EventBus()
    rec = []
    def handler(e):
        rec.append(e.copy())
    bus.subscribe(handler)
    bus.context_middleware()
    ev = {'device_id': 'dev1', 'firmware': '1.2.3'}
    bus.publish(ev)
    assert rec and '_context' in rec[0]
    ctx = rec[0]['_context']
    assert ctx['device_id'] == 'dev1'
    assert ctx['firmware'] == '1.2.3'
    assert 'trace' in ctx

def test_attach_logger():
    bus = EventBus()
    logs_info = []
    logs_error = []
    class Logger:
        def info(self, msg):
            logs_info.append(msg)
        def error(self, msg):
            logs_error.append(msg)
    logger = Logger()
    bus.attach_logger(logger)
    def handler(e):
        pass
    # subscribe and unsubscribe
    sub_id = bus.subscribe(handler)
    bus.unsubscribe(sub_id)
    # publish normal
    bus.subscribe(handler)
    bus.publish({'ok': True})
    # publish error
    def bad(e):
        raise Exception("bad")
    bus.subscribe(bad)
    bus.dead_letter_queue("dlq")
    bus.set_global_error_handler(lambda ex, ev: None)
    bus.publish({'bad': True})
    assert any("Subscribed handler" in msg for msg in logs_info)
    assert any("Unsubscribed handler" in msg for msg in logs_info)
    assert any("Scheduled" in msg or "Publishing" in msg or "Delivered" in msg for msg in logs_info)
    assert any("Error" in msg for msg in logs_error)
