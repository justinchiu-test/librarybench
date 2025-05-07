import pytest
import system_architect.schema_versioning as sv

def setup_function():
    # Clear registry before each test
    sv.registry._schemas.clear()

def test_register_and_get_schema():
    schema_v1 = {'a': 1, 'b': 2}
    sv.schema_versioning(schema_v1, 'v1')
    fetched = sv.registry.get_schema('v1')
    assert fetched == schema_v1
    # Modifying fetched copy should not affect registry
    fetched['a'] = 100
    assert sv.registry.get_schema('v1')['a'] == 1

def test_duplicate_registration_error():
    schema = {'x': 0}
    sv.schema_versioning(schema, 'v1')
    with pytest.raises(ValueError):
        sv.schema_versioning(schema, 'v1')

def test_migrate_add_fields_and_remove_extra():
    schema_v1 = {'a': 1, 'b': 2}
    schema_v2 = {'b': 20, 'c': 30}
    sv.schema_versioning(schema_v1, 'v1')
    sv.schema_versioning(schema_v2, 'v2')
    data = {'a': 10, 'b': 200, 'extra': 999}
    migrated = sv.migrate(data, 'v1', 'v2')
    # 'b' preserved, 'c' default, 'a' removed
    assert migrated == {'b': 200, 'c': 30}

def test_migrate_invalid_inputs_and_versions():
    with pytest.raises(KeyError):
        sv.migrate({'a':1}, 'no_v', 'v1')
    sv.schema_versioning({'a':1}, 'v1')
    with pytest.raises(KeyError):
        sv.migrate({'a':1}, 'v1', 'no_v')
    with pytest.raises(TypeError):
        sv.migrate('not a dict', 'v1', 'v1')
