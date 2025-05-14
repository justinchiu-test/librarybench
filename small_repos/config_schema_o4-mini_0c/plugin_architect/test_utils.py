import os
import tempfile
import pytest
from config_manager.utils import load_yaml, load_dotenv

def test_load_yaml(tmp_path):
    content = {"a": 1, "b": {"c": 2}}
    import yaml
    p = tmp_path / "test.yaml"
    p.write_text(yaml.safe_dump(content))
    data = load_yaml(str(p))
    assert data == content

def test_load_dotenv(tmp_path):
    p = tmp_path / ".env"
    p.write_text("""
# comment
KEY1=value1
KEY2 = value2
INVALIDLINE
""")
    data = load_dotenv(str(p))
    assert data == {"KEY1": "value1", "KEY2": "value2"}

def test_load_dotenv_missing(tmp_path):
    data = load_dotenv(str(tmp_path / "nope.env"))
    assert data == {}
