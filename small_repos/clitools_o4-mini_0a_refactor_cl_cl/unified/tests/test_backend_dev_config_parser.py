import json
import configparser
from backend_dev.microcli.config_parser import parse_config_files
import tempfile
import os

def test_parse_json(tmp_path):
    f = tmp_path / "c.json"
    f.write_text(json.dumps({"a": 1}))
    result = parse_config_files([str(f)])
    assert result["a"] == 1

def test_parse_ini(tmp_path):
    f = tmp_path / "c.ini"
    cp = configparser.ConfigParser()
    cp["sec"] = {"k": "v"}
    with open(f, "w") as fh:
        cp.write(fh)
    result = parse_config_files([str(f)])
    assert "sec" in result
    assert result["sec"]["k"] == "v"

def test_skip_unknown(tmp_path):
    f = tmp_path / "c.txt"
    f.write_text("ignore")
    assert parse_config_files([str(f)]) == {}
