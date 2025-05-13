import pytest
from config_manager.errors import ConfigError

def test_config_error_str():
    err = ConfigError(path=['a','b'], line=10, context="ctx", msg="fail")
    s = str(err)
    assert "fail" in s
    assert "path" in s
    assert "line=10" in s
    assert "context=ctx" in s
