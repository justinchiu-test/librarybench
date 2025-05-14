import pytest
import logging
from validation import Field, Schema, Validator, ValidationError
from validation.generator import TestDataGenerator
from validation.openapi import generate_openapi_schema

def strength_validator(pw):
    ok = len(pw) >= 8
    return ok, "Password too short" if not ok else ""

fields = [
    Field("username", str, required=True),
    Field("password", str, required=True, validators=[strength_validator]),
    Field("age", int, required=False, default=18),
    Field("email", str, required=True),
]
schema = Schema(fields)

def test_full_flow():
    # test data generation
    gen = TestDataGenerator.generate(schema)
    assert "username" in gen and "password" in gen
    # test validation failure
    v = Validator(schema)
    with pytest.raises(ValidationError):
        v.validate({"username": "u", "password": "short", "email": "a@b.com"})
    # test validation success
    valid = {"username": "user1", "password": "strongpass", "email": "a@b.com", "age": "25"}
    cleaned = v.validate(valid)
    assert cleaned["age"] == 25
    # test openapi output
    doc = generate_openapi_schema(schema, title="User")
    assert "User" in doc["components"]["schemas"]
