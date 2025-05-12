from config_manager.config import Config
from config_manager.profiles import ProfileManager

def test_profiles():
    base = Config().load_yaml("a: 1\nb: 2\n")
    dev = Config().load_yaml("b: 3\nc: 4\n")
    pm = ProfileManager(base)
    pm.add_profile('dev', dev)
    cfg_dev = pm.load('dev')
    assert cfg_dev.get('a') == 1
    assert cfg_dev.get('b') == 3
    assert cfg_dev.get('c') == 4
    cfg_unknown = pm.load('prod')
    assert cfg_unknown.get('a') == 1
    assert cfg_unknown.get('b') == 2
