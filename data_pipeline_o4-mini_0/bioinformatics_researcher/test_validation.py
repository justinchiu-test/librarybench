import pytest
from pipeline.validation import DataValidator, SchemaEnforcer

def test_data_validator():
    dv = DataValidator(['a', 'b'])
    assert dv.validate({'a': 1, 'b': 2})
    with pytest.raises(ValueError):
        dv.validate({'a': 1})

def test_schema_enforcer_valid():
    read = {'id': 'r1', 'seq': 'ACGT', 'quality': 30}
    assert SchemaEnforcer.enforce(read)

def test_schema_enforcer_invalid_missing():
    with pytest.raises(ValueError):
        SchemaEnforcer.enforce({'id': 'r1', 'seq': 'ACGT'})

def test_schema_enforcer_invalid_char():
    with pytest.raises(ValueError):
        SchemaEnforcer.enforce({'id': 'r1', 'seq': 'AXGT', 'quality': 30})
