import pytest
from config_loader.errors import ConfigError

def test_config_error_str_with_location_and_context():
    err = ConfigError("msg", file="f.py", line=10, context="here")
    s = str(err)
    assert "msg" in s
    assert "(f.py:10)" in s
    assert "Context: here" in s

def test_config_error_str_without_optional():
    err = ConfigError("msg")
    s = str(err)
    assert "msg" in s
