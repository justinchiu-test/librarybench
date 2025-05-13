import os
import json
import tempfile
import shutil
import configparser
import pytest

from config_manager import load_config, ConfigManager, expand_env_vars, ValidationError, with_config

yaml = pytest.importorskip("yaml")
jsonschema = pytest.importorskip("jsonschema")


def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)


def test_load_config_json(tmp_path):
    data = {"a": 1, "b": "text", "c": [1, 2, 3]}
    path = tmp_path / "conf.json"
    write_file(path, json.dumps(data))
    cfg = load_config(str(path))
    assert cfg == data


def test_load_config_ini(tmp_path):
    config = configparser.ConfigParser()
    config['sec'] = {'key': 'value', 'num': '5'}
    path = tmp_path / "conf.ini"
    with open(path, 'w') as f:
        config.write(f)
    cfg = load_config(str(path))
    assert 'sec' in cfg
    assert cfg['sec']['key'] == 'value'
    assert cfg['sec']['num'] == '5'


def test_load_config_yaml(tmp_path):
    data = {"x": "hello", "y": 2}
    path = tmp_path / "conf.yaml"
    write_file(path, yaml.dump(data))
    cfg = load_config(str(path))
    assert cfg == data


def test_caching(tmp_path):
    path = tmp_path / "c.json"
    write_file(path, json.dumps({"v": 1}))
    first = load_config(str(path))
    write_file(path, json.dumps({"v": 2}))
    second = load_config(str(path))
    # cache should update on mtime change
    assert second['v'] == 2


def test_expand_env_vars(tmp_path, monkeypatch):
    monkeypatch.setenv('TESTVAR', 'world')
    config = {"greet": "hello $TESTVAR", "nested": {"key": "${TESTVAR}!"}}
    expanded = expand_env_vars(config)
    assert expanded["greet"] == "hello world"
    assert expanded["nested"]["key"] == "world!"


def test_get_set(tmp_path):
    data = {"a": {"b": {"c": 3}}}
    path = tmp_path / "conf.json"
    write_file(path, json.dumps(data))
    mgr = ConfigManager(str(path))
    assert mgr.get("a.b.c") == 3
    assert mgr.get("a.b.x", 99) == 99
    mgr.set("a.b.d", 4)
    assert mgr.get("a.b.d") == 4
    mgr.set("new.key", "val")
    assert mgr.get("new.key") == "val"


def test_export_json_schema(tmp_path):
    data = {"a": 1, "b": "s", "c": [True, False], "d": {"x": 3.5}}
    path = tmp_path / "conf.json"
    write_file(path, json.dumps(data))
    mgr = ConfigManager(str(path))
    schema = mgr.export_json_schema()
    assert schema["properties"]["a"]["type"] == "integer"
    assert schema["properties"]["b"]["type"] == "string"
    assert schema["properties"]["c"]["type"] == "array"
    assert schema["properties"]["c"]["items"]["type"] == "boolean"
    assert schema["properties"]["d"]["type"] == "object"
    assert schema["properties"]["d"]["properties"]["x"]["type"] == "number"


def test_validate_types(tmp_path):
    data = {"num": 5, "name": "x"}
    schema = {
        "type": "object",
        "properties": {
            "num": {"type": "integer"},
            "name": {"type": "string"}
        },
        "required": ["num", "name"]
    }
    path = tmp_path / "conf.json"
    write_file(path, json.dumps(data))
    mgr = ConfigManager(str(path))
    # valid does not raise
    mgr.validate_types(schema)
    # invalid
    bad = {"num": "notint", "name": "x"}
    write_file(path, json.dumps(bad))
    mgr.reload()
    with pytest.raises(ValidationError) as exc:
        mgr.validate_types(schema)
    assert "expected" in str(exc.value)


def test_prompt_missing(tmp_path, monkeypatch):
    data = {"a": None, "b": {"c": ""}}
    path = tmp_path / "conf.json"
    write_file(path, json.dumps(data))
    mgr = ConfigManager(str(path))
    inputs = iter(["val1", "val2"])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    mgr.prompt_missing()
    assert mgr.get("a") == "val1"
    assert mgr.get("b.c") == "val2"


def test_with_config_decorator(tmp_path):
    data = {"key": "value"}
    path = tmp_path / "conf.json"
    write_file(path, json.dumps(data))

    @with_config(str(path))
    def func(cfg):
        return cfg.get("key")

    assert func() == "value"
