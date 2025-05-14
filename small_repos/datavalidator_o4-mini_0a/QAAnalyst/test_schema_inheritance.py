from datavalidation.schema_inheritance import SchemaInheritance

def test_extend_schema_base_none():
    si = SchemaInheritance()
    new_schema = si.extend_schema(999, {'required': ['x']})
    assert new_schema['required'] == ['x']

def test_extend_schema_merge():
    si = SchemaInheritance()
    new_schema = si.extend_schema(1, {'required': ['email'], 'optional': ['age']})
    assert 'email' in new_schema['required']
    assert 'age' in new_schema['optional']
