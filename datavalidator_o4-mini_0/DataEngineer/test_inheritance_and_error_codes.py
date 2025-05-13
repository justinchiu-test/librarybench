import pytest
from validator import Schema, Field, Validator

def test_inheritance_overrides():
    base = Schema(fields={'a': Field(int)})
    override = Field(int, optional=True)
    child = Schema(fields={'a': override, 'b': Field(str)}, bases=[base])
    v = Validator(child)
    # 'a' now optional
    res = v.validate_single({'b': 'hi'})
    assert res['valid']
    # missing b is error
    res2 = v.validate_single({'a': 1})
    assert not res2['valid']
    assert res2['errors'][0]['field'] == 'b'
