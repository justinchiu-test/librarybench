from config.base import nested_merge

def test_nested_merge_simple():
    a = {'x': 1, 'y': {'a': 10, 'b': 20}, 'z': [1,2,3]}
    b = {'y': {'b': 30, 'c': 40}, 'z': [4,5], 'w': 5}
    m = nested_merge(a, b)
    assert m['x'] == 1
    assert m['y']['a'] == 10
    assert m['y']['b'] == 30
    assert m['y']['c'] == 40
    assert m['z'] == [4,5]
    assert m['w'] == 5
