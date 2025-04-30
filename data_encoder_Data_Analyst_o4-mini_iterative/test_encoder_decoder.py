import pytest
from data_tools import encode, decode

def test_encode_decode_primitive():
    data = 42
    encoded = encode(data)
    assert isinstance(encoded, dict)
    assert encoded['type'] == 'primitive'
    assert encoded['value'] == 42
    assert encoded['value_type'] == 'int'
    decoded = decode(encoded)
    assert decoded == data

def test_homogeneous_primitive_list():
    data = [1, 2, 3, 4]
    encoded = encode(data)
    assert encoded['type'] == 'homogeneous_primitive_list'
    assert encoded['elem_type'] == 'int'
    assert encoded['data'] == data
    decoded = decode(encoded)
    assert decoded == data
    assert all(isinstance(x, int) for x in decoded)

def test_homogeneous_dict_list():
    data = [
        {'a': 1, 'b': 'x'},
        {'a': 2, 'b': 'y'}
    ]
    encoded = encode(data)
    assert encoded['type'] == 'homogeneous_dict_list'
    assert encoded['schema'] == {'a': 'int', 'b': 'str'}
    assert set(encoded['keys']) == set(['a', 'b'])
    sorted_keys = sorted(encoded['keys'])
    expected_values = [[d[k] for k in sorted_keys] for d in data]
    assert encoded['data'] == expected_values
    decoded = decode(encoded)
    assert decoded == data

def test_generic_list_mixed_types():
    data = [1, 'a', 3.14, False]
    encoded = encode(data)
    assert encoded['type'] == 'list'
    assert encoded['types'] == ['int', 'str', 'float', 'bool']
    assert encoded['data'] == data
    decoded = decode(encoded)
    assert decoded == data
    assert isinstance(decoded[3], bool)

def test_generic_dict():
    data = {'x': 10, 'y': 2.5, 'z': 'hello'}
    encoded = encode(data)
    assert encoded['type'] == 'dict'
    assert encoded['keys'] == ['x', 'y', 'z']
    assert encoded['types'] == ['int', 'float', 'str']
    assert encoded['values'] == [10, 2.5, 'hello']
    decoded = decode(encoded)
    assert decoded == data

def test_encode_unsupported_type():
    class Foo: pass
    data = Foo()
    with pytest.raises(ValueError):
        encode(data)
