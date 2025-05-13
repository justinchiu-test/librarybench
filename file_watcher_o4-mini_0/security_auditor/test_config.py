import pytest
import toml
import yaml
from pathlib import Path
from watcher.config import load_config

def write_file(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return p

def test_load_yaml(tmp_path):
    data = {"include": ["*.py"], "exclude": ["test_*"]}
    path = write_file(tmp_path, "conf.yaml", yaml.safe_dump(data))
    cfg = load_config(str(path))
    assert cfg == data

def test_load_toml(tmp_path):
    data = {"include": ["*.py"], "exclude": ["build/"]}
    toml_str = toml.dumps(data)
    path = write_file(tmp_path, "conf.toml", toml_str)
    cfg = load_config(str(path))
    assert cfg == data

def test_missing_keys(tmp_path):
    content = yaml.safe_dump({"include": ["*.py"]})
    path = write_file(tmp_path, "conf.yaml", content)
    with pytest.raises(ValueError):
        load_config(str(path))

def test_unsupported(tmp_path):
    path = write_file(tmp_path, "conf.txt", "dummy")
    with pytest.raises(ValueError):
        load_config(str(path))
