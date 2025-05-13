from datavalidation.single_validation import SingleItemValidation
from datavalidation.constraints import LengthConstraints, OptionalFields
from datavalidation.conditional_validation import ConditionalValidation

def test_single_validation_success():
    schema = {'required': ['id'], 'optional': ['note']}
    lc = LengthConstraints({'note': 5})
    of = OptionalFields(['note'], strict=False)
    sv = SingleItemValidation(schema, length_constraints=lc, optional_fields=of)
    result = sv.validate_single({'id': 1, 'note': 'hello'})
    assert result['valid']

def test_single_validation_missing_required():
    schema = {'required': ['id'], 'optional': []}
    sv = SingleItemValidation(schema)
    result = sv.validate_single({})
    assert not result['valid']
    assert result['errors'][0]['error'] == 'missing_field'

def test_single_validation_length_violation():
    schema = {'required': ['id'], 'optional': []}
    lc = LengthConstraints({'desc': 2})
    sv = SingleItemValidation(schema, length_constraints=lc)
    result = sv.validate_single({'id': 1, 'desc': 'abc'})
    assert not result['valid']
    assert any(e['error'] == 'length_exceeded' for e in result['errors'])

def test_single_validation_optional_strict():
    schema = {'required': ['id'], 'optional': ['note']}
    of = OptionalFields(['note'], strict=True)
    sv = SingleItemValidation(schema, optional_fields=of)
    result = sv.validate_single({'id': 1})
    assert not result['valid']
    assert result['errors'][0]['error'] == 'optional_missing'

def test_single_validation_conditional():
    schema = {'required': ['id'], 'optional': []}
    cv = ConditionalValidation()
    cv.add_condition('check', lambda r: [{'field': 'id'}] if r.get('id') != 0 else [])
    sv = SingleItemValidation(schema, conditional_validation=cv)
    result = sv.validate_single({'id': 1}, scenario='check')
    assert not result['valid']
    assert result['errors'][0]['error'] == 'conditional_failed'
