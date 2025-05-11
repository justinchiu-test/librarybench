import pytest
from unified.src.security_specialist import PluginManager

def test_register_and_get():
    pm = PluginManager()
    pm.register('rule', object())
    pm.register('rule', 'plugin2')
    plugins = pm.get('rule')
    assert len(plugins) == 2

def test_list_plugins():
    pm = PluginManager()
    pm.register('t1', 1)
    pm.register('t2', 2)
    lst = pm.list_plugins()
    assert 't1' in lst and 't2' in lst
