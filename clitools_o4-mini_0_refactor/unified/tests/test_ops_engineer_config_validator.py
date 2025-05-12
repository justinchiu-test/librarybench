import pytest
from ops_engineer.cli_toolkit.config_validator import validate_config

@pytest.fixture
def schema():
    return {
        "type": "object",
        "properties": {
            "a": {"type": "string"},
            "b": {"type": "integer"}
        },
        "required": ["a", "b"]
    }

def test_validate_success(schema):
    data = {"a": "foo", "b": 10}
    assert validate_config(schema, data) is True

def test_validate_missing_key(schema):
    with pytest.raises(ValueError):
        validate_config(schema, {"a": "foo"})

def test_validate_type_mismatch(schema):
    with pytest.raises(ValueError):
        validate_config(schema, {"a": "foo", "b": "bar"})
