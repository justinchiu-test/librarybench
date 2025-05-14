import pytest
from static_site_engine import to_json, from_json, to_yaml, from_yaml

def test_json_roundtrip():
    data = {"a": 1, "b": [1, 2, 3]}
    s = to_json(data)
    assert isinstance(s, str)
    out = from_json(s)
    assert out == data

def test_yaml_roundtrip():
    data = {"x": "value", "y": [True, False]}
    s = to_yaml(data)
    assert isinstance(s, str)
    out = from_yaml(s)
    assert out == data
