import pytest
from config_manager.merger import Merger

def test_scalar_override():
    m = Merger()
    base = {"a": 1}
    repo = {"a": 2}
    env = {"a": 3}
    res = m.merge(base, repo, env)
    assert res["a"] == 3

def test_nested_merge_and_list_append():
    m = Merger(list_strategy="append")
    base = {"list": [1], "nested": {"x": 1}}
    repo = {"list": [2], "nested": {"y": 2}}
    env = {"list": [3], "nested": {"x": 10}}
    res = m.merge(base, repo, env)
    assert res["list"] == [1,2,3]
    assert res["nested"]["x"] == 10
    assert res["nested"]["y"] == 2

def test_list_replace():
    m = Merger(list_strategy="replace")
    base = {"l": [0]}
    repo = {"l": [1,2]}
    env = {"l": [3]}
    res = m.merge(base, repo, env)
    assert res["l"] == [3]
