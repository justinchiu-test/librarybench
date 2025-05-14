import pytest
from scheduler.plugins import load_plugin, get_serializer_plugins, get_transport_plugins

class DummyPlugin:
    serializer = object()
    transport = object()

def test_load_plugin():
    before_ser = len(get_serializer_plugins())
    before_trans = len(get_transport_plugins())
    p = DummyPlugin()
    load_plugin(p)
    assert len(get_serializer_plugins()) == before_ser + 1
    assert len(get_transport_plugins()) == before_trans + 1
