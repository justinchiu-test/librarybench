import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from api_product_manager.contract_toolkit import (
    SchemaDiffTool, ErrorLocalization, PluginArchitecture,
    ValidationError, ProfileBasedRules, CoreDateTimeValidation,
    Schema, VersionedSchema, TransformationPipeline, SecureFieldMasking
)

def test_schema_diff_tool():
    old = {'a': 1, 'b': 2}
    new = {'b': 3, 'c': 4}
    diff = SchemaDiffTool.diff(old, new)
    assert set(diff['added']) == {'c'}
    assert set(diff['removed']) == {'a'}
    assert set(diff['changed']) == {'b'}

def test_error_localization():
    loc = ErrorLocalization()
    loc.register_backend('en', {'err': 'Error {code}'})
    loc.register_backend('es', {'err': 'Error Español {code}'})
    assert loc.translate('err', code=123) == 'Error 123'
    loc.set_language('es')
    assert loc.translate('err', code=456) == 'Error Español 456'
    assert loc.translate('missing') == 'missing'
    with pytest.raises(ValueError):
        loc.set_language('fr')

def test_plugin_architecture():
    pa = PluginArchitecture()
    pa.register_plugin('rules', 'r1', lambda x: x)
    pa.register_plugin('transforms', 't1', lambda x: x)
    rules = pa.get_plugins('rules')
    trans = pa.get_plugins('transforms')
    assert 'r1' in rules and callable(rules['r1'])
    assert 't1' in trans and callable(trans)
    with pytest.raises(ValueError):
        pa.register_plugin('unknown', 'u1', lambda x: x)
    with pytest.raises(ValueError):
        pa.get_plugins('unknown')

def test_profile_based_rules_sync_and_async():
    pr = ProfileBasedRules()
    def rule1(data):
        if data.get('x') != 1:
            raise ValidationError("x must be 1")
    async def rule2(data):
        await asyncio.sleep(0)
        if data.get('y') != 2:
            raise ValidationError("y must be 2")
    pr.add_rule('p', rule1)
    pr.add_rule('p', rule2)
    # both pass
    errs = asyncio.run(pr.validate('p', {'x':1,'y':2}))
    assert errs == []
    # fail both
    errs = asyncio.run(pr.validate('p', {'x':0,'y':0}))
    assert "x must be 1" in errs and "y must be 2" in errs

def test_core_datetime_validation():
    dt = CoreDateTimeValidation.parse_date("2020-01-01T12:00:00")
    assert isinstance(dt, datetime)
    custom = CoreDateTimeValidation.parse_date("01-02-2020", "%d-%m-%Y")
    assert custom.day == 2 and custom.month == 1
    # normalize
    naive = datetime(2020,1,1, tzinfo=None)
    norm = CoreDateTimeValidation.normalize(naive, timezone.utc)
    assert norm.tzinfo == timezone.utc
    # min/max
    base = datetime(2020,1,1, tzinfo=timezone.utc)
    assert CoreDateTimeValidation.check_min_max(base, min_date=base - timedelta(days=1))
    assert not CoreDateTimeValidation.check_min_max(base, max_date=base - timedelta(days=1))

def test_schema_inheritance():
    parent = Schema({'a':1, 'b':2})
    child = Schema({'b':3, 'c':4}, parent)
    assert child.fields == {'a':1, 'b':3, 'c':4}

def test_schema_versioning_and_migrations():
    vs = VersionedSchema({'a':1}, version=2)
    def mig(vdata):
        vdata['_version'] = 2
        vdata['b'] = 2
        return vdata
    vs.add_migration(1, mig)
    data = {'_version':1, 'a':1}
    migrated = vs.migrate(data, 2)
    assert migrated['_version'] == 2 and migrated['b'] == 2
    assert vs.validate_version({'_version':2})

def test_transformation_pipeline():
    tp = TransformationPipeline()
    tp.add(lambda x: x.strip())
    tp.add(lambda x: x.lower())
    assert tp.apply("  HeLLo ") == "hello"

def test_secure_field_masking():
    data = {'a':1, 'pwd':'secret', 'nested': {'pwd':'top', 'keep':2}, 'list':[{'pwd':'x'}]}
    masked = SecureFieldMasking.mask(data, ['pwd'])
    assert masked['a'] == 1
    assert masked['pwd'] == '***'
    assert masked['nested']['pwd'] == '***'
    assert masked['nested']['keep'] == 2
    assert masked['list'][0]['pwd'] == '***'
