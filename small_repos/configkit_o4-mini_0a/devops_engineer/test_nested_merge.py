from config_framework.nested_merge import nested_merge

def test_merge_simple():
    a = {'x': 1}
    b = {'y': 2}
    assert nested_merge(a, b) == {'x': 1, 'y': 2}

def test_merge_override():
    a = {'x': 1}
    b = {'x': 2}
    assert nested_merge(a, b)['x'] == 2

def test_merge_nested():
    a = {'svc': {'labels': {'env': 'prod'}, 'ports': [80]}}
    b = {'svc': {'labels': {'version': 'v1'}, 'ports': [8080]}}
    merged = nested_merge(a, b)
    assert merged['svc']['labels'] == {'env': 'prod', 'version': 'v1'}
    assert merged['svc']['ports'] == [8080]
