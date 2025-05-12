from config.merge import nested_merge

def test_nested_merge_simple():
    base = {'a': 1, 'b': {'c': 2}}
    override = {'b': {'d': 3}, 'e': 4}
    result = nested_merge(base, override)
    assert result == {'a':1, 'b':{'c':2,'d':3}, 'e':4}

def test_callbacks_override():
    base = {'callbacks': ['a','b'], 'x':1}
    override = {'callbacks': ['c'], 'x':2}
    result = nested_merge(base, override)
    assert result['callbacks'] == ['c']
    assert result['x'] == 2
