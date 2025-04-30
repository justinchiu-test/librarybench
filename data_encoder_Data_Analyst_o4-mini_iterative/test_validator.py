import pytest
from data_tools import validate

def test_validate_primitives():
    assert validate(5, {'type': 'int'})
    assert not validate(True, {'type': 'int'})  # bool is not int
    assert validate(True, {'type': 'bool'})
    assert validate(3.14, {'type': 'float'})
    assert validate('abc', {'type': 'str'})
    assert not validate(5, {'type': 'str'})

def test_validate_list():
    schema = {'type': 'list', 'schema': {'type': 'int'}}
    assert validate([1,2,3], schema)
    assert not validate([1, 'a', 3], schema)
    assert not validate('not a list', schema)
    # empty list is valid
    assert validate([], schema)
    # missing schema
    assert not validate([1,2], {'type': 'list'})

def test_validate_dict():
    schema = {
        'type': 'dict',
        'schema': {
            'a': {'type': 'int'},
            'b': {'type': 'str'},
            'c': {'type': 'list', 'schema': {'type': 'float'}}
        }
    }
    data = {'a': 10, 'b': 'hello', 'c': [1.1, 2.2]}
    assert validate(data, schema)
    # missing key
    bad_data = {'a': 10, 'b': 'hello'}
    assert not validate(bad_data, schema)
    # wrong type inside list
    bad_data2 = {'a': 10, 'b': 'hello', 'c': [1.1, 'x']}
    assert not validate(bad_data2, schema)
    # extra keys allowed
    extra = {'a': 1, 'b': 'x', 'c': [], 'd': 5}
    assert validate(extra, schema)
    # wrong type overall
    assert not validate(['not','a','dict'], schema)
