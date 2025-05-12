import json
import pytest
from security_analyst.cli_framework.config import load_config
from security_analyst.jsonschema import ValidationError

schema = {"type": "object", "properties": {"a": {"type": "number"}}, "required": ["a"]}

def test_load_json(tmp_path):
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps({"a": 1}))
    data = load_config(str(p), schema)
    assert data["a"] == 1

def test_load_yaml(tmp_path):
    import security_analyst.yaml as yaml
    p = tmp_path / "cfg.yaml"
    p.write_text("a: 2")
    data = load_config(str(p), schema)
    assert data["a"] == 2

def test_load_toml(tmp_path):
    import security_analyst.toml as toml
    p = tmp_path / "cfg.toml"
    p.write_text("a = 3")
    data = load_config(str(p), schema)
    assert data["a"] == 3

def test_invalid(tmp_path):
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps({"b": 2}))
    with pytest.raises(ValidationError):
        load_config(str(p), schema)
