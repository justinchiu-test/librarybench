import os
import tempfile
import json
import configparser
import pytest
from plugin_framework.config_loader import load_config

def test_load_json(tmp_path):
    data = {'a': 1, 'b': 'two'}
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    cfg = load_config(str(path))
    assert cfg == data

def test_load_ini(tmp_path):
    ini = configparser.ConfigParser()
    ini['sec'] = {'key': 'value'}
    path = tmp_path / "config.ini"
    with open(path, 'w') as f:
        ini.write(f)
    cfg = load_config(str(path))
    assert 'sec' in cfg
    assert cfg['sec']['key'] == 'value'

def test_load_unsupported(tmp_path):
    path = tmp_path / "conf.txt"
    path.write_text("data")
    with pytest.raises(ValueError):
        load_config(str(path))
