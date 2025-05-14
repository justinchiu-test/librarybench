import pytest
from validator import VersionedSchemas, Schema, Field, Validator

def test_no_version_field():
    vs = VersionedSchemas()
    schema = Schema(fields={'a': Field(int)})
    vs.register('nov', 1, schema)
    v = Validator(schema, version_name='nov', versioned_schemas=vs)
    rec = {'a': 1}
    result = v.validate_single(rec)
    assert result['valid']
    assert 'version' not in result['record']

def test_multiple_migrations():
    vs = VersionedSchemas()
    s1 = Schema(fields={'x': Field(int)})
    s2 = Schema(fields={'x': Field(int), 'y': Field(int, default=0)})
    s3 = Schema(fields={'x': Field(int), 'y': Field(int), 'z': Field(str, default='z')})
    vs.register('multi', 1, s1)
    vs.register('multi', 2, s2)
    vs.register('multi', 3, s3)
    vs.add_migration('multi', 1, 2, lambda r: {**r, 'y': 20})
    vs.add_migration('multi', 2, 3, lambda r: {**r, 'z': 'ok'})
    v = Validator(s3, version_name='multi', versioned_schemas=vs)
    rec = {'x': 7, 'version': 1}
    res = v.validate_single(rec)
    assert res['valid']
    assert res['record']['version'] == 3
    assert res['record']['y'] == 20
    assert res['record']['z'] == 'ok'
