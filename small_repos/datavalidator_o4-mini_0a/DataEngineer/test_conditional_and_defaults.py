import pytest
from validator import Schema, Field, Validator

def test_conditional_with_default():
    schema = Schema(fields={
        'val': Field(int, default=5, condition=lambda r: r.get('use_default', True))
    })
    v = Validator(schema)
    res1 = v.validate_single({'use_default': True})
    assert res1['valid']
    assert res1['record']['val'] == 5
    res2 = v.validate_single({'use_default': False})
    # condition false, skip default? default still applied before validate
    assert res2['valid']
    assert res2['record']['val'] == 5
