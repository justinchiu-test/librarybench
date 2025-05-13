from config_manager.merge import merge_configs

def test_merge_simple():
    a = {"x": 1, "y": 2}
    b = {"y": 3, "z": 4}
    res = merge_configs(a, b)
    assert res == {"x": 1, "y": 3, "z": 4}

def test_merge_nested():
    a = {"a": {"b": 1, "c": 2}}
    b = {"a": {"c": 3, "d": 4}}
    res = merge_configs(a, b)
    assert res == {"a": {"b":1, "c":3, "d":4}}
