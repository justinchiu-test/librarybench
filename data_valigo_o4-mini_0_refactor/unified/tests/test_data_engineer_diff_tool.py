import pytest
from unified.src.data_engineer.dataschema.diff_tool import SchemaDiffTool

def test_diff_added_removed_changed():
    old = {'a': int, 'b': str, 'c': float}
    new = {'b': str, 'c': int, 'd': bool}
    diff = SchemaDiffTool.diff(old, new)
    assert diff == {
        'added': ['d'],
        'removed': ['a'],
        'changed': ['c'],
    }
