import pytest
from nested_codec import validate_schema

def test_validate_simple_types():
    data = {"x": 10, "y": "foo"}
    schema = {"x": int, "y": str}
    assert validate_schema(data, schema)

def test_missing_and_extra_keys():
    data = {"x": 10}
    schema = {"x": int, "y": str}
    with pytest.raises(KeyError) as exc:
        validate_schema(data, schema)
    assert "missing keys" in str(exc.value)
    # extra key
    data2 = {"x": 10, "y": "bar", "z": 5}
    schema2 = {"x": int, "y": str}
    with pytest.raises(KeyError) as exc2:
        validate_schema(data2, schema2)
    assert "unexpected keys" in str(exc2.value)

def test_type_mismatch_error():
    data = {"x": "not int", "y": 5}
    schema = {"x": int, "y": int}
    with pytest.raises(TypeError) as exc:
        validate_schema(data, schema)
    assert "Expected type int at root.x" in str(exc.value)

def test_list_schema():
    data = {"lst": [1, 2, 3]}
    schema = {"lst": [int]}
    assert validate_schema(data, schema)
    # wrong element
    data2 = {"lst": [1, "two", 3]}
    with pytest.raises(TypeError) as exc2:
        validate_schema(data2, schema)
    assert "root.lst[1]" in str(exc2.value)

def test_tuple_schema():
    data = {"tup": ["a", "b"]}
    schema = {"tup": (str,)}
    assert validate_schema(data, schema)

def test_set_schema():
    data = {"s": {1,2,3}}
    schema = {"s": {"set": int}}
    assert validate_schema(data, schema)
    # wrong element type
    data2 = {"s": {1, "two"}}
    with pytest.raises(TypeError):
        validate_schema(data2, schema)

def test_schema_malformed():
    data = [1,2,3]
    # schema list with zero elements
    with pytest.raises(ValueError):
        validate_schema(data, [])
    # schema list with two elements
    with pytest.raises(ValueError):
        validate_schema(data, [int, str])
