from config_manager.schema import compose_schema

def test_compose_schema():
    s1 = {"a": 1, "b": {"x": 2}}
    s2 = {"b": {"y": 3}, "c": 4}
    res = compose_schema(s1, s2)
    assert res == {"a":1, "b":{"x":2,"y":3}, "c":4}
