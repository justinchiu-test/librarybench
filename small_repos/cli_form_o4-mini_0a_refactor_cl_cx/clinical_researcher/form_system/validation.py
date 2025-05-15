import re

# Specification for commonly used fields
SPEC = {
    'patient_id': {
        'regex': r'^[A-Za-z0-9]{6,12}$',
        'required': True,
    },
    'phone': {
        'regex': r'^\+?\d{10,15}$',
        'required': True,
    },
    'name': {
        'required': True,
        'max_length': 50,
    }
}

def validate_input(values):
    """
    Validate a dict of field values according to SPEC.
    Returns dict of field -> error message (only for fields that failed).
    """
    errors = {}
    for field, rules in SPEC.items():
        value = values.get(field, "")
        if rules.get('required') and not value:
            errors[field] = f"{field} is required"
            continue
        if 'regex' in rules and value:
            if not re.match(rules['regex'], value):
                errors[field] = f"{field} does not match required format"
        if 'max_length' in rules and value:
            if len(value) > rules['max_length']:
                errors[field] = f"{field} exceeds max length of {rules['max_length']}"
    return errors
