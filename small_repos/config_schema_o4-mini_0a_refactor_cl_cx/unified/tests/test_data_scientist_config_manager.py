import os
import json
import configparser
import pytest
import tempfile

import configschema as cm

def test_load_json(tmp_path):
    p = tmp_path / "conf.json"
    data = {"a": 1, "b": 2.5, "c": "hello", "d": [1,2,3], "e": "${TEST_VAR}"}
    p.write_text(json.dumps(data))
    os.environ["TEST_VAR"] = "world"
    cfg = cm.load_config(str(p))
    assert cfg.get("a") == 1 and isinstance(cfg.get("a"), int)
    assert cfg.get("b") == 2.5 and isinstance(cfg.get("b"), float)
    assert cfg.get("c") == "hello"
    assert cfg.get("d") == [1,2,3]
    assert cfg.get("e") == "world"

def test_load_ini(tmp_path):
    p = tmp_path / "conf.ini"
    ini = "[DEFAULT]\na=1\nb=2.5\nc=hello\nd=x,y,z\n"
    p.write_text(ini)
    cfg = cm.load_config(str(p))
    assert cfg.get("a") == 1 and isinstance(cfg.get("a"), int)
    assert cfg.get("b") == 2.5 and isinstance(cfg.get("b"), float)
    assert cfg.get("c") == "hello"
    assert cfg.get("d") == ["x","y","z"]

def test_load_yaml(tmp_path):
    if cm.yaml is None:
        pytest.skip("PyYAML not installed")
    p = tmp_path / "conf.yaml"
    content = """
    a: 10
    b:
      - 1
      - 2
    c:
      nested: true
    """
    p.write_text(content)
    cfg = cm.load_config(str(p))
    assert cfg.get("a") == 10
    assert cfg.get("b") == [1,2]
    assert cfg.get("c") == {"nested": True}

def test_get_set_and_validation(tmp_path):
    p = tmp_path / "conf.json"
    data = {"x": 5}
    p.write_text(json.dumps(data))
    cfg = cm.load_config(str(p))
    assert cfg.get("x") == 5
    cfg.set("x", 10)
    assert cfg.get("x") == 10
    with pytest.raises(cm.ValidationError):
        cfg.set("x", "notint")

def test_export_json_schema(tmp_path):
    p = tmp_path / "conf.json"
    data = {"i": 1, "f": 1.2, "s": "str", "l": [1,2]}
    p.write_text(json.dumps(data))
    cfg = cm.load_config(str(p))
    # instance export_json_schema returns dict
    schema = cfg.export_json_schema()
    assert schema["type"] == "object"
    props = schema["properties"]
    assert props["i"]["type"] == "integer"
    assert props["f"]["type"] == "number"
    assert props["s"]["type"] == "string"
    assert props["l"]["type"] == "array"
    assert props["i"]["default"] == 1

def test_with_config_decorator(tmp_path):
    p = tmp_path / "conf.json"
    data = {"lr": 0.01, "bs": 32}
    p.write_text(json.dumps(data))
    @cm.with_config(str(p))
    def train(lr: float, bs: int, momentum: float=0.9):
        return lr, bs, momentum
    result = train()
    assert result == (0.01, 32, 0.9)

def test_with_config_missing(monkeypatch, tmp_path):
    p = tmp_path / "conf.json"
    data = {"a": 1}
    p.write_text(json.dumps(data))
    inputs = iter(["2.5"])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    @cm.with_config(str(p))
    def f(a: int, b: float):
        return a, b
    result = f()
    assert result == (1, 2.5)

def test_caching(tmp_path):
    p = tmp_path / "conf.json"
    data = {"x": 1}
    p.write_text(json.dumps(data))
    cfg1 = cm.load_config(str(p))
    cfg2 = cm.load_config(str(p))
    assert cfg1 is cfg2

def test_validation_error_message():
    err = cm.ValidationError(file="f", line=10, section="sec", key="k", message="bad", suggestions=["a","b"])
    s = str(err)
    assert "File 'f'" in s
    assert "Line 10" in s
    assert "In section 'sec'" in s
    assert "Key 'k'" in s
    assert "bad" in s
    assert "Suggestions: a, b" in s
