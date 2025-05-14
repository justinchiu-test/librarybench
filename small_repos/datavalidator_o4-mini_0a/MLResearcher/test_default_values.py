from default_values import set_default_values

def test_set_default_values():
    schema = {'a': {'type': int, 'default': 10},
              'b': {'type': str}}
    record = {'a': None, 'b': 'hello'}
    filled = set_default_values(record, schema)
    assert filled['a'] == 10
    assert filled['b'] == 'hello'
