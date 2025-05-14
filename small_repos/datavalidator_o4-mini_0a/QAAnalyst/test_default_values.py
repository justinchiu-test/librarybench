from datavalidation.default_values import DefaultValues

def test_set_default_values():
    dv = DefaultValues()
    record = {'a': 1}
    defaults = {'a': 10, 'b': 2}
    new_record = dv.set_default_values(record, defaults)
    assert new_record['a'] == 1
    assert new_record['b'] == 2
