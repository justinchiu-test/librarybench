import pytest
from api_validator.versioned_schemas import VersionedSchemas

def test_register_and_get():
    vs = VersionedSchemas()
    schema = {'a': 1}
    vs.register(1, schema)
    assert vs.get(1) == schema

def test_migrate_same_version():
    vs = VersionedSchemas()
    data = {'x': 2}
    assert vs.migrate(data, 1, 1) == data

def test_migrate_other_version():
    vs = VersionedSchemas()
    with pytest.raises(NotImplementedError):
        vs.migrate({}, 1, 2)
