import pytest
from config_framework.core import merge_configs

def test_merge_overwrite_non_dict():
    a = {"x": 1}
    b = {"x": {"nested": True}}
    merged = merge_configs(a, b)
    assert merged["x"] == {"nested": True}

def test_merge_list_override():
    a = {"lst": [1, 2]}
    b = {"lst": [3]}
    # lists are not dicts, so override
    merged = merge_configs(a, b)
    assert merged["lst"] == [3]

def test_merge_deeply_nested():
    a = {"a": {"b": {"c": 1}}}
    b = {"a": {"b": {"d": 2}}}
    merged = merge_configs(a, b)
    assert merged["a"]["b"]["c"] == 1
    assert merged["a"]["b"]["d"] == 2

def test_merge_type_mismatch():
    a = {"k": "value"}
    b = {"k": {"sub": 1}}
    merged = merge_configs(a, b)
    assert merged["k"] == {"sub": 1}
