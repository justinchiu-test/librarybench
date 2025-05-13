import pytest
from pipeline.validation import DataValidator, SchemaEnforcer

def test_data_validator_success():
    schema = {'required':['a'], 'properties':{'a':{'type':int}}}
    v = DataValidator(schema)
    assert v.validate({'a':1})

def test_data_validator_fail_missing():
    schema = {'required':['a'], 'properties':{}}
    v = DataValidator(schema)
    with pytest.raises(ValueError):
        v.validate({'b':2})

def test_data_validator_fail_type():
    schema = {'required':[], 'properties':{'a':{'type':int}}}
    v = DataValidator(schema)
    with pytest.raises(ValueError):
        v.validate({'a':'string'})

def test_schema_enforcer_defaults():
    schema = {'properties':{'a':{'default':10}, 'b':{'default':'x'}}}
    e = SchemaEnforcer(schema)
    rec = {}
    out = e.enforce(rec)
    assert out['a'] == 10 and out['b'] == 'x'
