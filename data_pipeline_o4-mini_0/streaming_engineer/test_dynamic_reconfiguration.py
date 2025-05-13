from dynamic_reconfiguration import DynamicReconfiguration

def test_dynamic_reconfiguration():
    dr = DynamicReconfiguration({'a': 1})
    assert dr.get('a') == 1
    dr.update_config({'b': 2})
    assert dr.get('b') == 2
    dr.update_config({'a': 3})
    assert dr.get('a') == 3
