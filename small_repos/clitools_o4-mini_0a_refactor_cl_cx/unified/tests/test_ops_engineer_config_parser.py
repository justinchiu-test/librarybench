import pytest
from ops_engineer.cli_toolkit.config_parser import parse_config_string, merge_dicts

json_str = '{"a":1,"b":2}'
ini_str = "[section]\na=10\nb=20\n"
yaml_str = "x: 5\ny: true\n"
toml_str = "foo = \"bar\"\nnum = 3\n"

def test_parse_json():
    d = parse_config_string(json_str, 'json')
    assert d == {"a":1,"b":2}

def test_parse_ini():
    d = parse_config_string(ini_str, 'ini')
    assert "section" in d and d["section"]["a"] == "10"

def test_parse_yaml(tmp_path, monkeypatch):
    try:
        import yaml  # noqa
    except ImportError:
        pytest.skip("PyYAML not installed")
    d = parse_config_string(yaml_str, 'yaml')
    assert d["x"] == 5 and d["y"] == True

def test_parse_toml(tmp_path):
    try:
        import toml  # noqa
    except ImportError:
        pytest.skip("toml not installed")
    d = parse_config_string(toml_str, 'toml')
    assert d["foo"] == "bar" and d["num"] == 3

def test_merge_dicts():
    a = {'x':1, 'nested': {'a':1}}
    b = {'y':2, 'nested': {'b':2}}
    merged = merge_dicts(a, b)
    assert merged['x'] == 1
    assert merged['y'] == 2
    assert merged['nested']['a'] == 1 and merged['nested']['b'] == 2
