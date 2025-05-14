import pytest
from telemetry.schema import validate_schema

def test_validate_json_success():
    data = {'a':1, 'b':'x'}
    schema = {'properties': {'a': int, 'b': str}}
    assert validate_schema(data, schema) is True

def test_validate_json_missing():
    data = {'a':1}
    schema = {'properties': {'a': int, 'b': str}}
    with pytest.raises(ValueError):
        validate_schema(data, schema)

def test_validate_json_type_error():
    data = {'a':'wrong', 'b':'x'}
    schema = {'properties': {'a': int, 'b': str}}
    with pytest.raises(TypeError):
        validate_schema(data, schema)

def test_validate_binary_success():
    data = b'1234'
    schema = {'length': 4}
    assert validate_schema(data, schema) is True

def test_validate_binary_fail():
    data = b'12'
    schema = {'length': 4}
    with pytest.raises(ValueError):
        validate_schema(data, schema)
