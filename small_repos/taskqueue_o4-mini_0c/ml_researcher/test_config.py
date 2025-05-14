from scheduler.config import ConfigManager

def test_config_update_and_subscribe():
    cm = ConfigManager({'a':1})
    updates = []
    cm.subscribe(lambda cfg: updates.append(cfg.copy()))
    cm.update({'b':2})
    assert cm.get('a') == 1
    assert cm.get('b') == 2
    assert updates and updates[0]['b'] == 2
