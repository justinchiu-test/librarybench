import pytest
from scheduler.plugins import PluginManager

class DummyTransport:
    pass

class DummySerializer:
    pass

def test_plugin_registration_and_retrieval():
    pm = PluginManager()
    pm.register_transport("mqtt", DummyTransport)
    pm.register_serializer("json", DummySerializer)
    assert pm.get_transport("mqtt") is DummyTransport
    assert pm.get_serializer("json") is DummySerializer
    assert pm.get_transport("nope") is None
    assert pm.get_serializer("none") is None
