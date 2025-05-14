import json
import pytest
from config_manager import infer_schema

def test_infer_schema_simple():
    obj = {"a": 1, "b": "s", "c": True, "d": None}
    schema = infer_schema(obj)
    assert schema["type"] == "object"
    props = schema["properties"]
    assert props["a"]["type"] == "integer"
    assert props["b"]["type"] == "string"
    assert props["c"]["type"] == "boolean"
    assert props["d"]["type"] == "null"

def test_infer_schema_nested():
    obj = {"x": {"y": [1,2,3]}}
    schema = infer_schema(obj)
    assert schema["properties"]["x"]["type"] == "object"
    inner = schema["properties"]["x"]["properties"]["y"]
    assert inner["type"] == "array"
    assert inner["items"]["type"] == "integer"
