from scheduler.plugins import PluginRegistry

def test_plugin_registry():
    pr = PluginRegistry()
    pr.register_serializer('s1', lambda x: str(x))
    pr.register_reporter('r1', lambda x: x)
    pr.register_validator('v1', lambda x: True)
    assert pr.get_serializer('s1')('abc') == 'abc'
    assert pr.get_reporter('r1')(5) == 5
    assert pr.get_validator('v1')(None) is True
