import json
import configparser
from src.personas.backend_dev.microcli.config_parser import MicroserviceConfigParser
import tempfile
import os

def test_parse_json(tmp_path):
    f = tmp_path / "c.json"
    f.write_text(json.dumps({"a": 1}))
    parser = MicroserviceConfigParser(config_dir=str(tmp_path))
    result = parser.load_config("test")
    assert result["a"] == 1

def test_parse_ini(tmp_path):
    f = tmp_path / "test.ini"
    cp = configparser.ConfigParser()
    cp["sec"] = {"k": "v"}
    with open(f, "w") as fh:
        cp.write(fh)
    parser = MicroserviceConfigParser(config_dir=str(tmp_path))
    result = parser.load_config("test")
    assert "sec" in result
    assert result["sec"]["k"] == "v"

def test_skip_unknown(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("ignore")
    parser = MicroserviceConfigParser(config_dir=str(tmp_path))
    result = parser.load_config("test")
    # This should not contain the content from the text file
    assert "ignore" not in str(result)