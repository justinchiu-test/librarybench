from config_framework.conflict_reporting import ConflictReporting

def test_no_conflicts():
    d1 = {'a': 1, 'b': 2}
    d2 = {'a': 1, 'c': 3}
    conflicts = ConflictReporting.find_conflicts(d1, d2)
    assert conflicts == {}

def test_conflicts():
    d1 = {'a': 1, 'b': 2}
    d2 = {'a': 2, 'b': 2}
    d3 = {'a': 1, 'b': 3}
    conflicts = ConflictReporting.find_conflicts(d1, d2, d3)
    assert 'a' in conflicts and conflicts['a'] == {1, 2}
    assert 'b' in conflicts and conflicts['b'] == {2, 3}
