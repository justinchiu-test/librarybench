import pytest
from form_system.plugin import register_field_plugin, get_field_plugin

class DummyPlugin:
    pass

def test_plugin_registration():
    name = 'dummy'
    register_field_plugin(name, DummyPlugin)
    cls = get_field_plugin(name)
    assert cls is DummyPlugin

def test_plugin_duplicate():
    name = 'dup'
    register_field_plugin(name, DummyPlugin)
    with pytest.raises(KeyError):
        register_field_plugin(name, DummyPlugin)
