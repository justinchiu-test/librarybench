from streamkit.dynamic import DynamicReconfiguration

def test_dynamic_set_get():
    dr = DynamicReconfiguration()
    dr.set('threshold', 10)
    assert dr.get('threshold') == 10
    assert dr.get('missing') is None
