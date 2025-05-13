import os
import json
import pytest
from onboarding.config_loader import load_config

def test_load_json(tmp_path):
    data = {"a": 1, "b": "two"}
    p = tmp_path/"config.json"
    p.write_text(json.dumps(data))
    assert load_config(str(p)) == data

def test_load_ini(tmp_path):
    ini = "[section]\nkey=value\n"
    p = tmp_path/"config.ini"
    p.write_text(ini)
    cfg = load_config(str(p))
    assert cfg == {"section": {"key": "value"}}

def test_load_yaml(tmp_path):
    yaml_content = "section:\n  key: value\n"
    p = tmp_path/"config.yaml"
    p.write_text(yaml_content)
    try:
        from onboarding.config_loader import yaml
        if yaml is None:
            pytest.skip("YAML not installed")
    except ImportError:
        pytest.skip("YAML import error")
    result = load_config(str(p))
    assert result == {"section": {"key": "value"}}

def test_load_toml(tmp_path):
    toml_content = 'a = 1\n[b]\nc = "three"\n'
    p = tmp_path/"config.toml"
    p.write_text(toml_content)
    try:
        from onboarding.config_loader import toml
        if toml is None:
            pytest.skip("toml not installed")
    except ImportError:
        pytest.skip("toml import error")
    result = load_config(str(p))
    assert result["a"] == 1
    assert result["b"]["c"] == "three"

def test_unsupported():
    p = "file.unsupported"
    with pytest.raises(ValueError):
        load_config(p)
