from datavalidation.constraints import LengthConstraints, OptionalFields

def test_length_constraints_violation():
    limits = {'name': 3}
    lc = LengthConstraints(limits)
    violations = lc.check_length({'name': 'abcd'})
    assert violations and violations[0]['field'] == 'name'

def test_optional_fields_strict():
    of = OptionalFields(['x'], strict=True)
    violations = of.check_optional({})
    assert violations and violations[0]['field'] == 'x'

def test_optional_fields_lenient():
    of = OptionalFields(['x'], strict=False)
    violations = of.check_optional({})
    assert violations == []
