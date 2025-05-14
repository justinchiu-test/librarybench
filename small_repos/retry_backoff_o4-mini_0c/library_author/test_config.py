import json
import os
import pytest
from retry_framework.config import ConfigFileSupport

def test_load_json(tmp_path):
    data = {"key": "value", "num": 42}
    file_path = tmp_path / "config.json"
    file_path.write_text(json.dumps(data))
    loaded = ConfigFileSupport.load(str(file_path))
    assert loaded == data

def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        ConfigFileSupport.load("does_not_exist.json")

def test_load_unsupported_extension(tmp_path):
    file_path = tmp_path / "conf.txt"
    file_path.write_text("dummy")
    with pytest.raises(ValueError):
        ConfigFileSupport.load(str(file_path))

@pytest.mark.skipif(yaml is None, reason="PyYAML not installed")
def test_load_yaml(tmp_path):
    import yaml
    data = {"a": 1, "b": 2}
    file_path = tmp_path / "config.yaml"
    file_path.write_text(yaml.dump(data))
    loaded = ConfigFileSupport.load(str(file_path))
    assert loaded == data

@pytest.mark.skipif(toml is None, reason="toml not installed")
def test_load_toml(tmp_path):
    import toml
    data = {"x": 10, "y": 20}
    file_path = tmp_path / "config.toml"
    file_path.write_text(toml.dumps(data))
    loaded = ConfigFileSupport.load(str(file_path))
    assert loaded == data
