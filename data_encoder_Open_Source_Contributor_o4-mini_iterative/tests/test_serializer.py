import pytest
from serializer import encode, decode, nested_structure_support

def test_encode_primitives():
    assert encode(123) == "123"
    assert encode(1.23) == "1.23"
    assert encode(True) == "true"
    assert encode("abc") == "\"abc\""

def test_decode_primitives():
    assert decode("123") == 123
    assert decode("1.23") == 1.23
    assert decode("true") is True
    assert decode("\"abc\"") == "abc"

def test_roundtrip_various():
    samples = [
        0,
        -10,
        3.1415,
        False,
        "hello",
        [1, "two", True, 4.0],
        {"x": 1, "y": [2, 3], "z": {"nested": "yes"}},
        [],
        {}
    ]
    for item in samples:
        assert decode(encode(item)) == item

def test_nested_structure_support():
    data = {
        "a": [1, 2, {"b": "c", "d": [3, 4]}],
        "e": {"f": False, "g": [[], {"h": 7}]}
    }
    result = nested_structure_support(data)
    assert result == data

def test_decode_invalid():
    with pytest.raises(ValueError):
        decode("not a valid json")
