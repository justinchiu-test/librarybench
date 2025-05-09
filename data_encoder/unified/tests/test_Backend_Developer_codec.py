import pytest
import json
from nested_codec import (
    encode_nested_structures,
    decode_nested_structures,
    check_data_integrity
)

def test_encode_decode_primitives_and_containers():
    data = {
        "number": 123,
        "text": "hello",
        "flag": True,
        "none": None,
        "list": [1, 2, 3],
        "tuple": ("a", "b"),
        "dict": {"x": 10, "y": "z"},
    }
    encoded = encode_nested_structures(data)
    assert isinstance(encoded, bytes)
    # Integrity should pass
    assert check_data_integrity(encoded)
    # Decode should recover original (tuples become lists)
    decoded = decode_nested_structures(encoded)
    assert decoded["number"] == 123
    assert decoded["text"] == "hello"
    assert decoded["flag"] is True
    assert decoded["none"] is None
    assert decoded["list"] == [1, 2, 3]
    assert decoded["tuple"] == ["a", "b"]
    assert decoded["dict"] == {"x": 10, "y": "z"}

def test_sets_are_encoded_and_decoded():
    data = {
        "ints": {1, 2, 3},
        "empty": set()
    }
    encoded = encode_nested_structures(data)
    decoded = decode_nested_structures(encoded)
    assert decoded["ints"] == {1, 2, 3}
    assert isinstance(decoded["ints"], set)
    assert decoded["empty"] == set()

def test_nested_structures():
    data = {"root": [ {"a": {1,2}}, {"b":[{"c":set()}]} ]}
    encoded = encode_nested_structures(data)
    decoded = decode_nested_structures(encoded)
    assert decoded == data

def test_check_data_integrity_false_on_tampering():
    original = {"a": 1}
    encoded = encode_nested_structures(original)
    # Tamper: change one char in the payload
    s = encoded.decode()
    s_tampered = s.replace("1", "2", 1)
    assert not check_data_integrity(s_tampered)
    # decode should raise
    with pytest.raises(ValueError):
        decode_nested_structures(s_tampered)

def test_check_data_integrity_invalid_json():
    assert not check_data_integrity("not a json")

