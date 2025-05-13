import pytest
from schema_validator import SchemaValidator

schema = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string', 'minLength': 2, 'maxLength': 5},
        'flag': {'type': 'boolean'}
    },
    'required': ['id', 'name'],
    'optional': ['flag']
}
aliases = {'identifier': 'id'}

def test_strict_mode_extra_field():
    validator = SchemaValidator(schema, strict_mode=True)
    errors = validator.validate({'id': 1, 'name': 'ab', 'extra': 123})
    assert any('Unexpected field extra' in e['message'] for e in errors)

def test_permissive_mode_extra_field():
    validator = SchemaValidator(schema, strict_mode=False)
    errors = validator.validate({'id': 1, 'name': 'ab', 'extra': 123})
    assert not errors

def test_optional_fields_toggle():
    validator = SchemaValidator(schema, optional_fields=False)
    errors = validator.validate({'id': 1, 'name': 'ab'})
    assert any('Missing required field flag' in e['message'] for e in errors)

def test_data_coercion():
    validator = SchemaValidator(schema, data_coercion=True)
    errors = validator.validate({'id': '2', 'name': 'abc', 'flag': 'true'})
    assert not errors

def test_alias_fields():
    validator = SchemaValidator(schema, aliases=aliases)
    errors = validator.validate({'identifier': 5, 'name': 'hello'})
    assert not errors

def test_aggregated_error_reporting():
    validator = SchemaValidator(schema)
    errors = validator.validate({'id': 'x', 'name': 'a', 'flag': 123})
    assert len(errors) >= 3
    paths = [e['path'] for e in errors]
    assert 'id' in paths
    assert 'name' in paths
    assert 'flag' in paths
