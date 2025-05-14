import pytest
from config_manager.config import Config

def test_load_and_get_set():
    cfg = Config()
    cfg.load_yaml("ui:\n  theme:\n    primaryColor: '#ff0000'\n")
    assert cfg.get("ui.theme.primaryColor") == "#ff0000"
    cfg.set("ui.theme.primaryColor", "#00ff00")
    assert cfg.get("ui.theme.primaryColor") == "#00ff00"

def test_nested_merge_and_conflicts():
    a = Config().load_yaml("features:\n  android:\n    dark_mode: false\nlanguages:\n  - en\n")
    b = Config().load_yaml("features:\n  android:\n    dark_mode: true\nlanguages:\n  - es\n")
    a.merge(b)
    assert a.get("features.android.dark_mode") == True
    assert "features.android.dark_mode" in a.conflicts
    # languages list fallback merge
    assert set(a.get("languages")) == {"en","es"}

def test_interpolation():
    cfg = Config().load_yaml("""
API_HOST: api.example.com
endpoint: http://${API_HOST}/v1
features:
  os: android
  android:
    dark_mode: true
  ios:
    dark_mode: false
flag: ${features.${features.os}.dark_mode}
""")
    assert cfg.get("endpoint") == "http://api.example.com/v1"
    assert cfg.get("flag") == "true"

def test_default_get():
    cfg = Config()
    assert cfg.get("nonexistent", "default") == "default"
    assert cfg.get("nonexistent") is None

def test_visualize():
    cfg = Config().load_yaml("a:\n  b:\n    c: 1\n")
    viz = cfg.visualize()
    lines = viz.splitlines()
    assert "a" in lines and "  b" in lines and "    c" in lines
