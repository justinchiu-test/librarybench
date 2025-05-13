import pytest
from version_schemas import VersionedSchemas

def test_add_and_get_schema():
    vs = VersionedSchemas()
    schema_v1 = {'a': int}
    vs.add_schema(1, schema_v1)
    assert vs.get_schema(1) == schema_v1

def test_migration_success():
    vs = VersionedSchemas()
    data_v1 = {'x': 1}
    def mig(d): return {'x': d['x'] + 1}
    vs.add_migration(1, 2, mig)
    result = vs.migrate(data_v1, 1, 2)
    assert result['x'] == 2

def test_migration_noop():
    vs = VersionedSchemas()
    data = {'x': 5}
    assert vs.migrate(data, 2, 2) == data

def test_migration_missing():
    vs = VersionedSchemas()
    with pytest.raises(ValueError):
        vs.migrate({'x':0}, 1, 3)
