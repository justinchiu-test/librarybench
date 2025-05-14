import pytest
from pipeline import validate_schema

def test_validate_schema_success():
    record = {"a": 1, "b": 2}
    schema = {"required": ["a", "b"]}
    assert validate_schema(record, schema) is True

def test_validate_schema_missing():
    record = {"a": 1}
    schema = {"required": ["a", "b"]}
    with pytest.raises(ValueError) as exc:
        validate_schema(record, schema)
    assert "Missing required fields" in str(exc.value)
