import pytest
from clinical_researcher.form_system.validation import validate_input

def test_validate_input_success():
    vals = {
        'patient_id': 'ABC123',
        'phone': '+12345678901',
        'name': 'John Doe'
    }
    errors = validate_input(vals)
    assert errors == {}

def test_validate_input_missing_required():
    vals = {
        'patient_id': '',
        'phone': '',
        'name': ''
    }
    errors = validate_input(vals)
    assert 'patient_id' in errors
    assert 'phone' in errors
    assert 'name' in errors

def test_validate_input_bad_format():
    vals = {
        'patient_id': 'ABC!',  # too short and bad char
        'phone': '12345',
        'name': 'A' * 51
    }
    errors = validate_input(vals)
    assert errors['patient_id'].startswith('patient_id does not match')
    assert errors['phone'].startswith('phone does not match')
    assert errors['name'].startswith('name exceeds max length')
