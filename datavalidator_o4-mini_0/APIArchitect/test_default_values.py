from api_validator.default_values import DefaultValues

def test_apply_defaults():
    dv = DefaultValues()
    schema = {'a': {'default': 10}, 'b': {}}
    data = {}
    result = dv.apply_defaults(data, schema)
    assert result['a'] == 10
    assert 'b' not in result
