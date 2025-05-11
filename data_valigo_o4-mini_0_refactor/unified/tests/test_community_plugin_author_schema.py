import pytest
from unified.src.community_plugin_author import Schema, VersionedSchema

def test_schema_inheritance_and_validation():
    parent = Schema({'a': int, 'b': str})
    child = Schema({'b': int, 'c': float}, parent=parent)
    data = {'a': 1, 'b': 2, 'c': 3.0}
    assert child.validate(data) is True
    with pytest.raises(ValueError):
        child.validate({'a':1, 'b':2})  # missing c

def test_versioned_schema_migration():
    vs = VersionedSchema({'x': int}, version=1)
    # migration from 1 to 2: add y
    def mig(data):
        data['y'] = 10
        return data
    vs.add_migration(1, mig)
    data = {'x':5}
    migrated = vs.migrate(data, 2)
    assert migrated['y'] == 10
    # missing migration back
    with pytest.raises(ValueError):
        vs.migrate(data, 0)
