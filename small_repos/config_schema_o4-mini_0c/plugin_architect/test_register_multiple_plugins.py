from config_manager.plugin import register_plugin, get_plugins

def p1(x): return x
def p2(x): return x

def test_multiple_hooks():
    register_plugin(validators=p1)
    register_plugin(validators=p2)
    vals = get_plugins('validators')
    assert p1 in vals and p2 in vals
