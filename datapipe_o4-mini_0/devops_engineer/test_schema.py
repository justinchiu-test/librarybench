import pytest
from pipeline.schema import validate_schema

def test_validate_schema_success():
    payload = {'a': 1, 'b': 2}
    schema = {'required': ['a', 'b']}
    assert validate_schema(payload, schema)

def test_validate_schema_failure():
    payload = {'a': 1}
    schema = {'required': ['a', 'b']}
    with pytest.raises(ValueError) as exc:
        validate_schema(payload, schema)
    assert 'Missing required field: b' in str(exc.value)
