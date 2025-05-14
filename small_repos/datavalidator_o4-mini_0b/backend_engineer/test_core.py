import pytest
import logging
from validation import Field, Schema, Validator, ValidationError, FieldError
from validation.plugins import corporate_email_plugin

def email_validator(v):
    return (v.endswith("@example.com"), "Email must be @example.com")

fields = [
    Field("firstName", str, required=True, alias="first_name"),
    Field("age", int, required=True),
    Field("middleName", str, required=False, default=""),
    Field("phoneNumber", str, required=False),
    Field("email", str, required=True, validators=[email_validator]),
]

schema = Schema(fields)

def test_valid_payload(caplog):
    caplog.set_level(logging.INFO)
    v = Validator(schema)
    payload = {"first_name": "Alice", "age": "30", "email": "alice@example.com"}
    cleaned = v.validate(payload)
    assert cleaned["firstName"] == "Alice"
    assert isinstance(cleaned["age"], int) and cleaned["age"] == 30
    assert cleaned["middleName"] == ""
    assert "phoneNumber" not in cleaned or cleaned["phoneNumber"] is None
    assert "Validation succeeded" in caplog.text

def test_missing_required():
    v = Validator(schema)
    payload = {"age": 25, "email": "bob@example.com"}
    with pytest.raises(ValidationError) as e:
        v.validate(payload)
    errs = e.value.errors
    assert any(err.path == "firstName" for err in errs)

def test_default_optional():
    v = Validator(schema)
    payload = {"first_name": "Cathy", "age": 22, "email": "cathy@example.com"}
    cleaned = v.validate(payload)
    assert cleaned["middleName"] == ""

def test_alias_and_coercion():
    v = Validator(schema)
    payload = {"first_name": "Dave", "age": "45", "email": "dave@example.com"}
    cleaned = v.validate(payload)
    assert cleaned["firstName"] == "Dave"
    assert isinstance(cleaned["age"], int)

def test_extra_field_strict():
    v = Validator(schema, strict=True)
    payload = {"first_name": "Eve", "age": 29, "email": "eve@example.com", "extra": "nope"}
    with pytest.raises(ValidationError) as e:
        v.validate(payload)
    errs = e.value.errors
    assert any("Unexpected field" in err.message for err in errs)

def test_extra_field_permissive():
    v = Validator(schema, strict=False)
    payload = {"first_name": "Frank", "age": 40, "email": "frank@example.com", "extra": "ok"}
    cleaned = v.validate(payload)
    assert cleaned["extra"] == "ok"

def test_aggregated_errors():
    v = Validator(schema)
    payload = {"first_name": "", "age": "NaN", "email": "bademail"}
    with pytest.raises(ValidationError) as e:
        v.validate(payload)
    errs = e.value.errors
    paths = {err.path for err in errs}
    assert "age" in paths and "email" in paths

def test_custom_validator():
    v = Validator(schema)
    payload = {"first_name": "Gus", "age": 55, "email": "gus@wrong.com"}
    with pytest.raises(ValidationError) as e:
        v.validate(payload)
    errs = e.value.errors
    assert any("Email must be @example.com" in err.message for err in errs)

def test_plugin_integration():
    plugin = corporate_email_plugin("corp.com")
    v = Validator(schema, plugins=[plugin])
    payload = {"first_name": "Hank", "age": 60, "email": "hank@other.com"}
    with pytest.raises(ValidationError) as e:
        v.validate(payload)
    errs = e.value.errors
    assert any("Email must end with @corp.com" in err.message for err in errs)
