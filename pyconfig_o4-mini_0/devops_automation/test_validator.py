import pytest
from config_manager.validator import validate
from config_manager.errors import ConfigError

schema = {
    "type": "object",
    "properties": {
        "age": {"type": "integer"},
        "name": {"type": "string"}
    },
    "required": ["age", "name"]
}

def test_validate_success():
    config = {"age": 30, "name": "Alice"}
    # should not raise
    validate(config, schema)

def test_validate_failure():
    config = {"age": "thirty"}
    with pytest.raises(ConfigError) as exc:
        validate(config, schema)
    assert "Validation failed" in str(exc.value)
    assert "age" in str(exc.value)
