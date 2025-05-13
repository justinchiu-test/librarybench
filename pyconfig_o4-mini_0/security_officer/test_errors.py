import pytest
from config_framework.errors import ConfigError

def test_config_error_attributes():
    err = ConfigError("msg", "file.py", 10)
    assert "msg" in str(err)
    assert err.file == "file.py"
    assert err.line == 10

def test_raise_config_error():
    with pytest.raises(ConfigError) as e:
        raise ConfigError("bad", "x", 1)
    assert e.value.file == "x"
    assert e.value.line == 1
