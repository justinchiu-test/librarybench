import os
import json
import configparser
import pytest

from config_manager import (
    load_config, load_json, load_ini, load_yaml, expand_env_vars,
    export_json_schema, ConfigManager, ValidationError, with_config, _cache
)

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def test_load_json(tmp_path):
    data = {"a": 1, "b": {"c": 2}}
    path = tmp_path / "cfg.json"
    write_file(path, json.dumps(data))
    cfg = load_config(str(path))
    assert cfg == data
    # caching
    assert str(path) in _cache
    cfg2 = load_config(str(path))
    assert cfg is cfg2

def test_load_ini(tmp_path):
    content = """
    [section1]
    key1 = value1
    num = 10
    """
    path = tmp_path / "cfg.ini"
    write_file(path, content)
    cfg = load_config(str(path))
    assert cfg['section1']['key1'] == 'value1'
    assert cfg['section1']['num'] == '10'

def test_load_yaml(tmp_path):
    if load_yaml is None:
        pytest.skip("No YAML support")
    content = """
    root:
      child: hello
      num: 5
    """
    path = tmp_path / "cfg.yaml"
    write_file(path, content)
    cfg = load_config(str(path))
    assert cfg['root']['child'] == 'hello'
    assert cfg['root']['num'] == 5

def test_expand_env_vars(tmp_path, monkeypatch):
    monkeypatch.setenv('HOST', 'localhost')
    monkeypatch.setenv('PORT', '8080')
    data = {"url": "http://${HOST}:${PORT}/api", "noenv": "plain"}
    path = tmp_path / "env.json"
    write_file(path, json.dumps(data))
    cfg = load_config(str(path))
    assert cfg['url'] == "http://localhost:8080/api"
    assert cfg['noenv'] == "plain"

def test_export_json_schema(tmp_path):
    data = {"x": 1, "y": "test", "z": [1,2,3]}
    path = tmp_path / "sch.json"
    write_file(path, json.dumps(data))
    schema = export_json_schema(str(path))
    assert schema['type'] == 'object'
    props = schema['properties']
    assert props['x']['type'] == 'integer'
    assert props['y']['type'] == 'string'
    assert props['z']['type'] == 'array'
    assert 'items' in props['z']

def test_validate_types_success(tmp_path):
    data = {"a": 10, "b": "s"}
    path = tmp_path / "vt.json"
    write_file(path, json.dumps(data))
    cm = ConfigManager(str(path))
    cm.validate_types()  # should not raise

def test_validate_types_error(tmp_path):
    data = {"a": 10, "b": "s"}
    path = tmp_path / "vt2.json"
    write_file(path, json.dumps(data))
    cm = ConfigManager(str(path))
    cm.set("a", "wrong")
    with pytest.raises(ValidationError) as exc:
        cm.validate_types()
    err = exc.value
    assert err.file == str(path)
    assert err.key == "a"
    assert err.expected == "integer"
    assert err.actual == "str"

def test_get_set(tmp_path):
    data = {"one": 1}
    path = tmp_path / "gs.json"
    write_file(path, json.dumps(data))
    cm = ConfigManager(str(path))
    assert cm.get("one") == 1
    cm.set("two.inner", "val")
    assert cm.get("two.inner") == "val"
    with pytest.raises(KeyError):
        cm.get("missing")

def test_prompt_missing(tmp_path, monkeypatch):
    data = {"a": 1}
    path = tmp_path / "pm.json"
    write_file(path, json.dumps(data))
    cm = ConfigManager(str(path), prompt=True)
    monkeypatch.delenv('CI', raising=False)
    monkeypatch.setattr('builtins.input', lambda prompt: "userval")
    val = cm.get("new.key", prompt_missing=True)
    assert val == "userval"
    assert cm.get("new.key") == "userval"

def test_with_config(tmp_path):
    data = {"k": "v"}
    path = tmp_path / "wc.json"
    write_file(path, json.dumps(data))
    @with_config(str(path))
    def func(config=None):
        return config.get("k")
    assert func() == "v"
