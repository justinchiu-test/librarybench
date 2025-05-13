from optional_fields import make_optional, is_optional

def test_optional_fields():
    schema = {'a': {'type': int}, 'b': {'type': str}}
    schema2 = make_optional(schema, 'a')
    assert is_optional(schema2['a'])
    assert not is_optional(schema2['b'])
