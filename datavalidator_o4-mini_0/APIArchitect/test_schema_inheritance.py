from api_validator.schema_inheritance import SchemaInheritance

def test_extend_schema():
    base = {'a': 1, 'b': 2}
    overrides = {'b': 3, 'c': 4}
    result = SchemaInheritance.extend_schema(base, overrides)
    assert result == {'a': 1, 'b': 3, 'c': 4}
