import json
import pytest
from pathlib import Path
from sync_tool.config import Config

def test_load_json(tmp_path):
    cfg_path = tmp_path / "config.json"
    data = {'key': 'value'}
    cfg_path.write_text(json.dumps(data))
    cfg = Config(str(cfg_path))
    assert cfg.get('key') == 'value'
    assert cfg.get('missing', 'default') == 'default'

def test_load_missing():
    with pytest.raises(FileNotFoundError):
        Config('nonexistent.json')

def test_load_unsupported(tmp_path):
    file = tmp_path / "config.txt"
    file.write_text("data")
    with pytest.raises(ValueError):
        Config(str(file))
