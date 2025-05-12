import pytest
from feature_pipeline.schema import validate_schema

def test_validate_schema_pass():
    schema = {"type":"object","properties":{"x":{"type":"number"}},"required":["x"]}
    instance = {"x":1}
    assert validate_schema(instance, schema) is True

def test_validate_schema_fail():
    schema = {"type":"object","properties":{"x":{"type":"number"}},"required":["x"]}
    instance = {"x":"bad"}
    with pytest.raises(Exception):
        validate_schema(instance, schema)
