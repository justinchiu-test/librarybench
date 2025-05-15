import pytest
from security_officer.incident_form.plugins import register_field_plugin, get_plugin

class DummyPlugin:
    pass

def test_plugin_registration_and_retrieval():
    register_field_plugin("dummy", DummyPlugin)
    p = get_plugin("dummy")
    assert p is DummyPlugin

def test_plugin_duplicate():
    import security_officer.incident_form.plugins as mods
    with pytest.raises(ValueError):
        register_field_plugin("dummy", DummyPlugin)
