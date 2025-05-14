import pytest
from validator import Field, Schema, VersionedSchemas, Validator, PerformanceMetrics

def test_required_field_missing():
    schema = Schema(fields={'name': Field(str)})
    v = Validator(schema)
    result = v.validate_single({})
    assert not result['valid']
    assert len(result['errors']) == 1
    err = result['errors'][0]
    assert err['field'] == 'name'
    assert err['code'] == 'ERR_REQUIRED'

def test_type_mismatch():
    schema = Schema(fields={'age': Field(int)})
    v = Validator(schema)
    result = v.validate_single({'age': '30'})
    assert not result['valid']
    err = result['errors'][0]
    assert err['field'] == 'age'
    assert 'Expected type int' in err['message']
    assert err['code'] == 'ERR_TYPE_MISMATCH'

def test_default_value_assignment():
    schema = Schema(fields={
        'name': Field(str),
        'active': Field(bool, default=True)
    })
    v = Validator(schema)
    result = v.validate_single({'name': 'Bob'})
    assert result['valid']
    assert result['record']['active'] is True

def test_optional_field():
    schema = Schema(fields={
        'note': Field(str, optional=True)
    })
    v = Validator(schema)
    result = v.validate_single({})
    assert result['valid']
    assert 'note' not in result['record'] or result['record']['note'] is None

def test_length_constraints():
    schema = Schema(fields={
        'code': Field(str, min_length=3, max_length=5)
    })
    v = Validator(schema)
    too_short = v.validate_single({'code': 'hi'})
    assert not too_short['valid']
    assert too_short['errors'][0]['code'] == 'ERR_LENGTH_MIN'
    too_long = v.validate_single({'code': 'toolong'})
    assert not too_long['valid']
    assert too_long['errors'][0]['code'] == 'ERR_LENGTH_MAX'
    just_right = v.validate_single({'code': 'hey'})
    assert just_right['valid']

def test_conditional_validation():
    schema = Schema(fields={
        'x': Field(int, condition=lambda r: r.get('flag', False))
    })
    v = Validator(schema)
    # flag False, skip validation, so missing x is okay
    res1 = v.validate_single({'flag': False})
    assert res1['valid']
    # flag True, missing x is error
    res2 = v.validate_single({'flag': True})
    assert not res2['valid']
    assert res2['errors'][0]['field'] == 'x'

def test_schema_inheritance():
    base = Schema(fields={'a': Field(int)})
    child = Schema(fields={'b': Field(int)}, bases=[base])
    v = Validator(child)
    res = v.validate_single({'a': 1, 'b': 2})
    assert res['valid']
    missing = v.validate_single({'a': 1})
    assert not missing['valid']
    assert missing['errors'][0]['field'] == 'b'

def test_versioned_schema_and_migration():
    vs = VersionedSchemas()
    schema_v1 = Schema(fields={'a': Field(int)})
    schema_v2 = Schema(fields={'a': Field(int), 'b': Field(int, default=0)})
    vs.register('test', 1, schema_v1)
    vs.register('test', 2, schema_v2)
    vs.add_migration('test', 1, 2, lambda r: {**r, 'b': 10})
    v = Validator(schema_v2, version_name='test', versioned_schemas=vs)
    rec = {'a': 5, 'version': 1}
    result = v.validate_single(rec)
    assert result['valid']
    assert result['record']['version'] == 2
    assert result['record']['b'] == 10

def test_batch_validation_and_summary():
    schema = Schema(fields={'id': Field(int)})
    v = Validator(schema)
    records = [{'id': 1}, {'id': 'two'}, {}]
    summary = v.validate_batch(records)
    assert summary['total'] == 3
    assert summary['passed'] == 1
    assert summary['failed'] == 2
    assert isinstance(summary['errors'], list)
    assert len(summary['errors']) == 3

def test_performance_metrics_capture():
    schema = Schema(fields={'x': Field(int, optional=True)})
    v = Validator(schema, capture_performance=True)
    records = [{'x': i} for i in range(5)]
    summary = v.validate_batch(records)
    assert 'metrics' in summary
    metrics = summary['metrics']
    assert metrics['total_records'] == 5
    assert metrics['total_time'] >= 0

def test_custom_error_codes():
    schema = Schema(fields={
        'n': Field(int, error_codes={'type': 'CUSTOM_TYPE'})
    })
    v = Validator(schema)
    res = v.validate_single({'n': 'wrong'})
    assert not res['valid']
    err = res['errors'][0]
    assert err['code'] == 'CUSTOM_TYPE'
