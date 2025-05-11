import pytest
from unified.src.security_specialist import SchemaDiffTool

def test_diff_added_removed_changed():
    old = {'a': 1, 'b': 2, 'c': 3}
    new = {'b': 2, 'c': 4, 'd': 5}
    diff = SchemaDiffTool.diff(old, new)
    assert diff['added'] == {'d': 5}
    assert diff['removed'] == {'a': 1}
    assert diff['changed'] == {'c': {'old': 3, 'new': 4}}
