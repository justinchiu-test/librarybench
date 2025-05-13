import pytest
from config_loader.json_schema import export_schema, validate_schema
import jsonschema

def test_export_schema_identity():
    schema = {'type': 'object'}
    assert export_schema(schema) is schema

def test_validate_schema_success():
    schema = {'type': 'object', 'properties': {'a': {'type': 'number'}}, 'required': ['a']}
    validate_schema({'a': 1}, schema)

def test_validate_schema_failure():
    schema = {'type': 'object', 'properties': {'a': {'type': 'number'}}, 'required': ['a']}
    with pytest.raises(jsonschema.ValidationError):
        validate_schema({'a': 'x'}, schema)
