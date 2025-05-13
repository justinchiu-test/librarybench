import pytest
from cli_framework.config import load_config
import json, toml, yaml

def write_file(tmp_path, name, content):
    f = tmp_path / name
    f.write_text(content)
    return str(f)

def test_load_json(tmp_path):
    data = {"key": "value"}
    path = write_file(tmp_path, "config.json", json.dumps(data))
    assert load_config(path) == data

def test_load_yaml(tmp_path):
    data = {"key": "value"}
    path = write_file(tmp_path, "config.yaml", yaml.dump(data))
    assert load_config(path) == data

def test_load_toml(tmp_path):
    data = {"key": "value"}
    toml_content = toml.dumps(data)
    path = write_file(tmp_path, "config.toml", toml_content)
    assert load_config(path) == data

def test_load_ini(tmp_path):
    ini = "[default]\na=1\nb=two\n"
    path = write_file(tmp_path, "config.ini", ini)
    res = load_config(path, profile="default")
    assert res == {"a": "1", "b": "two"}

def test_load_ini_all(tmp_path):
    ini = "[one]\na=1\n[two]\nb=2\n"
    path = write_file(tmp_path, "config.ini", ini)
    res = load_config(path)
    assert "one" in res and "two" in res

def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config("noexist.json")
