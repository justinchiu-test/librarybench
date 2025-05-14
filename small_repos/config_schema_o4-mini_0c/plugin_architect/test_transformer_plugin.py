from config_manager.plugin import register_plugin, get_plugins

def t(x): return x*2

def test_transformer_registration():
    register_plugin(transformers=t)
    ts = get_plugins('transformers')
    assert t in ts
