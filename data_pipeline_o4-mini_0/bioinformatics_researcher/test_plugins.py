import pytest
from pipeline.plugins import PluginManager

def test_plugin_manager():
    pm = PluginManager()
    pm.register('double', lambda x: x * 2)
    assert 'double' in pm.list_plugins()
    assert pm.execute('double', 3) == 6
    with pytest.raises(KeyError):
        pm.execute('unknown', None)
