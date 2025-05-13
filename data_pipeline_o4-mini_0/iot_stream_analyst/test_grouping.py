from streamkit.grouping import BuiltInGroup

def test_grouping():
    items = ['a1','a2','b1']
    g = BuiltInGroup()
    res = g.group(items, key_fn=lambda x: x[0])
    assert res == {'a': ['a1','a2'], 'b': ['b1']}
