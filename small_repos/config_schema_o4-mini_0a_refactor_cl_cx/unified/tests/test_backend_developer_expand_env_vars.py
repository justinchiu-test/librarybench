import os
from configschema import expand_env_vars
def test_expand_simple(tmp_path, monkeypatch):
    monkeypatch.setenv("VAR1", "hello")
    data = {"a": "$VAR1", "b": "start_${VAR1}_end", "c": ["$VAR1", {"d": "$VAR1"}]}
    out = expand_env_vars(data)
    assert out["a"] == "hello"
    assert out["b"] == "start_hello_end"
    assert out["c"][0] == "hello"
    assert out["c"][1]["d"] == "hello"
