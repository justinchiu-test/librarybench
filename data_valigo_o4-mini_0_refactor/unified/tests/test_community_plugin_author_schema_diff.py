import pytest
from unified.src.community_plugin_author import SchemaDiffTool

def test_compute_diff_added_removed_changed():
    s1 = {'a': int, 'b': str, 'c': float}
    s2 = {'b': str, 'c': int, 'd': bool}
    diff = SchemaDiffTool.compute_diff(s1, s2)
    assert diff['added'] == {'d': bool}
    assert diff['removed'] == {'a': int}
    assert diff['changed'] == {'c': (float, int)}
