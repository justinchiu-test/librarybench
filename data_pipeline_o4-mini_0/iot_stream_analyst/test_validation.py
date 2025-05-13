import pytest
from streamkit.validation import DataValidation, SchemaEnforcement

def test_data_validation():
    schema = {'required': ['a'], 'properties': {'a': int, 'b': str}}
    dv = DataValidation(schema)
    assert dv.validate({'a':1, 'b':'x'}) is True
    assert dv.validate({'b':'x'}) is False
    assert dv.validate({'a':1, 'b':2}) is False

def test_schema_enforcement_success():
    schema = {'required': ['a'], 'properties': {'a': int, 'b': str}}
    se = SchemaEnforcement(schema)
    data = {'a': '2', 'b': 3}
    # 'a' casts to int, 'b' casts to str
    assert se.validate(data) is True
    assert isinstance(data['a'], int)
    assert isinstance(data['b'], str)

def test_schema_enforcement_failure():
    schema = {'required': ['a'], 'properties': {'a': int}}
    se = SchemaEnforcement(schema)
    with pytest.raises(ValueError):
        se.validate({'b': 2})
    with pytest.raises(ValueError):
        se.validate({'a': 'notint'})
