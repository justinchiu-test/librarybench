import os
import json
import tempfile
import pytest
import builtins

from configschema import (
    load_config, load_yaml, ConfigManager, ValidationError,
    export_json_schema, with_config, _cache
)
import configschema as configtool

# Helper to write files
def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def test_load_json(tmp_path):
    p = tmp_path / "test.json"
    data = {"a": 1, "b": {"c": "foo"}}
    write_file(str(p), json.dumps(data))
    cm = load_config(str(p))
    assert isinstance(cm, ConfigManager)
    assert cm.get("a") == 1
    assert cm.get("b.c") == "foo"

def test_load_ini(tmp_path):
    p = tmp_path / "test.ini"
    content = "[section]\nx=10\ny=hello"
    write_file(str(p), content)
    cm = load_config(str(p))
    assert cm.get("section.x") == "10"
    assert cm.get("section.y") == "hello"

@pytest.mark.skipif(load_yaml is None, reason="No yaml")
def test_load_yaml(tmp_path):
    p = tmp_path / "test.yaml"
    content = "host: 127.0.0.1\nport: 22\nnested:\n  flag: true"
    write_file(str(p), content)
    cm = load_config(str(p))
    assert cm.get("host") == "127.0.0.1"
    assert cm.get("nested.flag") is True or cm.get("nested.flag") == "true"

def test_cache(tmp_path):
    p = tmp_path / "test.json"
    data = {"k": "v"}
    write_file(str(p), json.dumps(data))
    _cache.clear()
    cm1 = load_config(str(p))
    cm2 = load_config(str(p))
    assert cm1 is cm2

def test_get_set():
    cm = ConfigManager({}, "f")
    cm.set("x.y.z", 5)
    assert cm.get("x.y.z") == 5
    assert cm.get("x.y") == {"z": 5}

def test_expand_env_vars(monkeypatch):
    monkeypatch.setenv("MYVAR", "VALUE")
    cm = ConfigManager({"a": "$MYVAR", "b": "no", "c": ["${MYVAR}", "$UNKNOWN"]}, "f")
    cm.expand_env_vars()
    assert cm.get("a") == "VALUE"
    assert cm.get("b") == "no"
    assert cm.get("c")[0] == "VALUE"
    assert "$UNKNOWN" in cm.get("c")[1]

def test_validate_types_success():
    cm = ConfigManager({"ip": "192.168.1.1", "port": 8080, "flag": True, "tok": "abc"}, "f")
    cm.validate_types({"ip": "ip", "port": "port", "flag": "bool", "tok": "token"})

def test_validate_types_fail():
    cm = ConfigManager({"ip": "not_ip", "p": 70000}, "f")
    with pytest.raises(ValidationError) as e:
        cm.validate_types({"ip": "ip"})
    ve = e.value
    assert "IP address" in str(ve)
    with pytest.raises(ValidationError):
        cm.validate_types({"p": "port"})

def test_export_json_schema():
    data = {"x": 1, "y": "s", "z": [True, False], "w": {"u": 5}}
    cm = ConfigManager(data, "f")
    schema = cm.export_json_schema()
    assert schema["type"] == "object"
    assert schema["properties"]["x"]["type"] == "integer"
    assert schema["properties"]["y"]["type"] == "string"
    assert schema["properties"]["z"]["type"] == "array"
    assert schema["properties"]["w"]["type"] == "object"

def test_prompt_missing(monkeypatch):
    inputs = iter(["val1", "val2"])
    monkeypatch.setattr(builtins, "input", lambda prompt: next(inputs))
    cm = ConfigManager({}, "f")
    cm.prompt_missing(["a", "b"])
    assert cm.get("a") == "val1"
    assert cm.get("b") == "val2"

def test_with_config(tmp_path):
    p = tmp_path / "cfg.json"
    data = {"num": 2}
    write_file(str(p), json.dumps(data))
    @with_config
    def add(cfg, x):
        return cfg.get("num") + x
    assert add(str(p), 3) == 5

def test_load_yaml_function_missing(monkeypatch):
    # temporarily remove yaml
    # simulate missing YAML support in loader
    # simulate missing YAML support in loader
    monkeypatch.setattr('configschema.loader.yaml', None)
    with pytest.raises(ImportError):
        load_yaml("no.yaml")
