import json
import tempfile
import os
from retry_framework.config import ConfigFileSupport

def test_load_json(tmp_path):
    data = {'a': 1, 'b': 2}
    path = tmp_path / 'conf.json'
    path.write_text(json.dumps(data))
    loaded = ConfigFileSupport.load(str(path))
    assert loaded == data

def test_load_unsupported():
    import pytest
    with pytest.raises(ValueError):
        ConfigFileSupport.load('conf.txt')
