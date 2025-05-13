import pytest
import datetime
from scheduler.plugins import PluginManager

class DummySerializer:
    def __call__(self, context):
        return f"serialized:{context['task'].name}"

class DummyTransport:
    def __init__(self):
        self.sent = []
    def send(self, message, context):
        self.sent.append((message, context))

def test_register_and_get_serializer():
    pm = PluginManager()
    pm.register_serializer('dummy', DummySerializer())
    serializer = pm.get_serializer('dummy')
    assert isinstance(serializer, DummySerializer)

def test_register_and_get_transport():
    pm = PluginManager()
    dt = DummyTransport()
    pm.register_transport('dummy', dt)
    transport = pm.get_transport('dummy')
    assert transport is dt

def test_serializer_transport_integration(monkeypatch):
    from scheduler.scheduler import Scheduler, Task
    pm = PluginManager()
    serializer = DummySerializer()
    transport = DummyTransport()
    pm.register_serializer('dummy', serializer)
    pm.register_transport('dummy', transport)
    sched = Scheduler()
    sched.plugin_manager = pm
    def action(context):
        raise AssertionError("Should not call default action")
    task = Task(
        name="test",
        action=action,
        schedule=datetime.datetime.now(),
        plugin_serializer='dummy',
        plugin_transport='dummy',
    )
    sched.register_task(task)
    due = sched.run_pending()
    assert len(due) == 1
    assert transport.sent, "Transport should have sent message"
    msg, ctx = transport.sent[0]
    assert msg == f"serialized:{task.name}"
    assert ctx['task'] is task
