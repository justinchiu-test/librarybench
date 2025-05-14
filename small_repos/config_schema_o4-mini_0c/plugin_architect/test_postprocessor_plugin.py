from config_manager.plugin import register_plugin, get_plugins

def p(x): return x

def test_postprocessor_registration():
    register_plugin(postprocessors=p)
    ps = get_plugins('postprocessors')
    assert p in ps
