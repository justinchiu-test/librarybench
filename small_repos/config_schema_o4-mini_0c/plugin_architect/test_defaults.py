from config_manager.api import ConfigManager

def test_default_factory():
    cm = ConfigManager()
    cm.set_default_factory("now", lambda: 123)
    assert cm.get("now") == 123
    assert cm.get("missing", default=0) == 0
