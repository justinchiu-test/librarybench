import pytest
from src.personas.backend_dev.microcli.config_validator import validate_config

schema = {
    "type": "object",
    "properties": {"x": {"type": "number"}, "y": {"type": "string"}},
    "required": ["x", "y"]
}

def test_valid_config():
    cfg = {"x": 1, "y": "yes"}
    assert validate_config(cfg, schema)

def test_missing_key():
    cfg = {"x": 1}
    assert not validate_config(cfg, schema)

def test_type_mismatch():
    cfg = {"x": "1", "y": "yes"}
    assert not validate_config(cfg, schema)

def test_invalid_schema_type():
    with pytest.raises(ValueError):
        validate_config({}, {"type": "array"})
