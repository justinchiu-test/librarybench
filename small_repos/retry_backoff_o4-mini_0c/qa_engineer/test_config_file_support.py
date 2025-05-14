import os
import json
import pytest
from retry_toolkit.config_file_support import ConfigFileSupport

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

def test_load_json(tmp_path):
    data = {"a": 1, "b": 2}
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    loaded = ConfigFileSupport.load_config(str(path))
    assert loaded == data

@pytest.mark.skipif(not HAVE_YAML, reason="YAML not available")
def test_load_yaml(tmp_path):
    import yaml
    data = {"x": 10, "y": 20}
    path = tmp_path / "config.yaml"
    path.write_text(yaml.dump(data))
    loaded = ConfigFileSupport.load_config(str(path))
    assert loaded == data

def test_invalid_config(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("not valid")
    with pytest.raises(ValueError):
        ConfigFileSupport.load_config(str(path))
