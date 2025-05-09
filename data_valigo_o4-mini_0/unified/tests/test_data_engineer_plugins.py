import pytest
from data_engineer.dataschema.plugins import PluginManager

def test_plugin_registration_and_retrieval():
    pm = PluginManager()
    pm.register('p1', object())
    pm.register('p2', 123)
    assert set(pm.list()) == {'p1', 'p2'}
    assert isinstance(pm.get('p1'), object)
    assert pm.get('nonexistent') is None
