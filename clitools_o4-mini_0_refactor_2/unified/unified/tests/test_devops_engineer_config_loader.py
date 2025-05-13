import json
import configparser
import os
import pytest
from adapters.devops_engineer.devops_cli.config_loader import load_config
import adapters.devops_engineer.devops_cli.toml as toml
import adapters.devops_engineer.devops_cli.yaml as yaml

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)

def test_load_all(tmp_path):
    ini = tmp_path / "a.ini"
    cp = configparser.ConfigParser()
    cp["sec"] = {"k": "v1"}
    with open(ini, "w") as f:
        cp.write(f)
    jsonf = tmp_path / "b.json"
    json.dump({"sec": {"k": "v2"}}, open(jsonf, "w"))
    yml = tmp_path / "c.yaml"
    yaml.safe_dump({"sec2": {"x": 1}}, open(yml, "w"))
    tomlf = tmp_path / "d.toml"
    toml.dump({"sec3": {"y": 2}}, open(tomlf, "w"))
    cfg = load_config([str(ini), str(jsonf), str(yml), str(tomlf)])
    assert cfg["sec"]["k"] == "v2"
    assert cfg["sec2"]["x"] == 1
    assert cfg["sec3"]["y"] == 2