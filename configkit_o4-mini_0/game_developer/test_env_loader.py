import os
from config.loaders import EnvLoader

def test_env_loader(tmp_path, monkeypatch):
    monkeypatch.setenv('GAME_GRAPHICS__SHADOW_QUALITY', 'high')
    monkeypatch.setenv('GAME_UI_SCALE', '1.5')
    cfg = EnvLoader.load()
    assert cfg['graphics']['shadow_quality'] == 'high'
    assert cfg['ui']['scale'] == '1.5'
