import pytest
from pipeline.schema import validate_schema

def test_validate_schema_success():
    data = {'a': 1, 'b': 'x'}
    schema = {
        'required': ['a'],
        'properties': {'a': {'type': 'number'}, 'b': {'type': 'string'}}
    }
    assert validate_schema(data, schema)

def test_validate_schema_missing():
    data = {'b': 'x'}
    schema = {'required': ['a'], 'properties': {'a': {'type': 'number'}}}
    with pytest.raises(ValueError):
        validate_schema(data, schema)

def test_validate_schema_custom():
    data = {'a': 2}
    def cust(d): return d['a'] > 1
    schema = {
        'required': ['a'],
        'properties': {'a': {'type': 'number'}},
        'custom': cust
    }
    assert validate_schema(data, schema)
    data2 = {'a': 1}
    with pytest.raises(ValueError):
        validate_schema(data2, schema)
