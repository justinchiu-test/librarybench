import pytest
import json

from Software_Developer.serializer.serializer import (
    custom_type_support,
    encoding,
    decoding,
    cross_language_support,
)
from Software_Developer.serializer.config import decoding_configuration, decoding_settings
from Software_Developer.serializer.lazy import LazyList

# ---------- Tests for primitive types ----------

@pytest.mark.parametrize("data", [
    123,
    45.67,
    "a string",
    True,
    False,
    None,
    [1, 2, 3],
    {"x": 1, "y": [2, 3]},
])
def test_encode_decode_primitives(data):
    s = encoding(data)
    result = decoding(s)
    assert result == data

# ---------- Tests for custom types ----------

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y
    def __repr__(self):
        return f"Point({self.x},{self.y})"

def encode_point(p):
    return {"x": p.x, "y": p.y}

def decode_point(d):
    return Point(d["x"], d["y"])

def test_custom_type_roundtrip():
    # Register custom type
    custom_type_support(Point, encode_point, decode_point)
    p = Point(10, 20)
    s = encoding({"pt": p, "msg": "hello"})
    decoded = decoding(s)
    assert isinstance(decoded["pt"], Point)
    assert decoded["pt"] == p
    assert decoded["msg"] == "hello"

# ---------- Tests for decoding configuration (lazy) ----------

def test_lazy_list_top_level():
    data = [1, 2, 3, 4]
    s = encoding(data)
    decoding_configuration({"lazy": True})
    assert decoding_settings["lazy"] is True
    result = decoding(s)
    assert isinstance(result, LazyList)
    # Check contents
    assert list(result) == data
    # Reset
    decoding_configuration({"lazy": False})

def test_lazy_nested_lists():
    data = {"a": [1, 2], "b": {"c": [3, 4]}}
    s = encoding(data)
    decoding_configuration({"lazy": True})
    result = decoding(s)
    # Top-level 'a' is LazyList
    assert isinstance(result["a"], LazyList)
    assert list(result["a"]) == [1, 2]
    # Nested list also LazyList
    assert isinstance(result["b"]["c"], LazyList)
    assert list(result["b"]["c"]) == [3, 4]
    # Reset
    decoding_configuration({"lazy": False})

# ---------- Tests for cross-language support ----------

def test_cross_language_support_valid_json():
    data = {"foo": "bar", "nums": [1,2,3]}
    s = cross_language_support(data, format="json")
    # Confirm it's valid JSON and matches original on simple types
    reloaded = json.loads(s)
    assert reloaded == data

def test_unsupported_format_encoding():
    with pytest.raises(ValueError):
        encoding({"x":1}, format="xml")

def test_unsupported_format_decoding():
    invalid = "<xml></xml>"
    with pytest.raises(ValueError):
        decoding(invalid, format="xml")

def test_unsupported_format_cross_language():
    with pytest.raises(ValueError):
        cross_language_support(123, format="msgpack")

# ---------- Tests for error conditions ----------

def test_decoding_configuration_bad_type():
    with pytest.raises(ValueError):
        decoding_configuration("not a dict")
