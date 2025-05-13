from schema_inheritance import extend_schema

def test_extend_schema_simple():
    base = {'a': {'type': int, 'default': 0}, 'b': {'type': float}}
    overrides = {'b': {'default': 1.0}, 'c': {'type': str}}
    ext = extend_schema(base, overrides)
    assert ext['a'] == {'type': int, 'default': 0}
    assert ext['b'] == {'type': float, 'default': 1.0}
    assert ext['c'] == {'type': str}
