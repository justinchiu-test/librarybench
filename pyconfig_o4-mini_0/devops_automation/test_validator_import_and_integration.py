# Integration test for json_schema_support
import pytest
from config_manager import validate_config
from config_manager.errors import ConfigError

schema = {"type": "object", "properties": {"x": {"type": "number"}}, "required": ["x"]}

def test_integration_valid():
    validate_config({"x": 1.5}, schema)

def test_integration_invalid():
    with pytest.raises(ConfigError):
        validate_config({"x": "no"}, schema)
