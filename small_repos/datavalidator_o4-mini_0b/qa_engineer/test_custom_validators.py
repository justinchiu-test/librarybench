from custom_validators import payment_limit_validator
from schema_validator import SchemaValidator

def test_payment_limit_validator():
    schema = {
        'type': 'object',
        'properties': {'amount': {'type': 'integer'}},
        'required': ['amount']
    }
    cv = payment_limit_validator(100)
    validator = SchemaValidator(schema, custom_validators=[cv])
    errors = validator.validate({'amount': 150})
    assert errors
    assert errors[0]['path'] == 'amount'
