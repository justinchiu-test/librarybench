import os
import json
import tempfile
import pytest
import logging
from game_developer.settings_manager import SettingsManager

def test_namespace_and_set_get():
    sm = SettingsManager()
    sm.namespace('graphics.shaders')
    assert 'graphics' in sm.config
    assert 'shaders' in sm.config['graphics']
    sm.set('graphics.shaders.type', 'phong')
    assert sm.get('graphics.shaders.type') == 'phong'

def test_validation_hook():
    sm = SettingsManager()
    sm.add_validation_hook('physics.gravity', lambda v: -20 <= v <= 0)
    sm.set('physics.gravity', -9.8)
    assert sm.get('physics.gravity') == -9.8
    with pytest.raises(ValueError):
        sm.set('physics.gravity', -100)

def test_export_to_json():
    sm = SettingsManager()
    sm.set('ai.behavior', 'aggressive')
    js = sm.export_to_json()
    data = json.loads(js)
    assert data['ai']['behavior'] == 'aggressive'

def test_hot_reload_json(tmp_path):
    sm = SettingsManager()
    data = {"graphics": {"resolution": "1024x768"}}
    fp = tmp_path / "test.json"
    fp.write_text(json.dumps(data))
    sm.hot_reload(str(fp))
    assert sm.get('graphics.resolution') == '1024x768'

def test_load_yaml(tmp_path, monkeypatch):
    yaml_content = "physics:\n  speed: 123\n"
    fp = tmp_path / "test.yaml"
    fp.write_text(yaml_content)
    sm = SettingsManager()
    # If yaml is available
    if sm.load_yaml:
        data = sm.load_yaml(str(fp))
        assert data['physics']['speed'] == 123
    # Simulate missing yaml
    monkeypatch.setattr('settings_manager.yaml', None)
    with pytest.raises(ImportError):
        sm.load_yaml(str(fp))

def test_load_envvars(monkeypatch):
    sm = SettingsManager()
    monkeypatch.setenv('GAME__DEBUG', 'true')
    monkeypatch.setenv('GAME__MAX_PLAYERS', '4')
    sm.load_envvars(prefix='GAME_')
    assert sm.get('debug') is True
    assert sm.get('max.players') == 4

def test_cache_invalidation_and_enabled():
    sm = SettingsManager()
    counter = {'count': 0}
    def loader():
        counter['count'] += 1
        return counter['count']
    sm.enable_cache('level1', loader)
    val1 = sm.get_cache('level1')
    val2 = sm.get_cache('level1')
    assert val1 == val2 == 1
    sm.set('some.setting', 1)
    val3 = sm.get_cache('level1')
    assert val3 == 2

def test_lazy_load():
    sm = SettingsManager()
    loaded = {'done': False}
    def loader():
        loaded['done'] = True
        return "heavy"
    sm.lazy_load('assets.level1', loader)
    assert not loaded['done']
    val = sm.get('assets.level1')
    assert loaded['done'] and val == "heavy"
    # subsequent get comes from config
    loaded['done'] = False
    assert sm.get('assets.level1') == "heavy"
    assert not loaded['done']

def test_parse_cli_args():
    sm = SettingsManager()
    args = ['--graphics.volume=75', '--physics.gravity=-9']
    sm.parse_cli_args(args)
    assert sm.get('graphics.volume') == 75
    assert sm.get('physics.gravity') == -9

def test_setup_logging():
    sm = SettingsManager()
    handler = logging.StreamHandler()
    sm.setup_logging(level=logging.DEBUG, handler=handler)
    assert sm.logger.level == logging.DEBUG
    assert handler in sm.logger.handlers
