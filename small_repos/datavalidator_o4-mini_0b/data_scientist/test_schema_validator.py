import pytest
from schema_validator.schema_validator import Field, SchemaValidator, ValidationError

def test_basic_validation_and_coercion():
    schema = [
        Field("a", int),
        Field("b", float),
        Field("c", bool),
        Field("d", str, optional=True, default="x")
    ]
    validator = SchemaValidator(schema)
    data = {"a": "10", "b": "2.5", "c": "true"}
    sanitized, errors = validator.validate(data)
    assert sanitized == {"a": 10, "b": 2.5, "c": True, "d": "x"}
    assert errors == []

def test_missing_required():
    schema = [Field("a", int)]
    validator = SchemaValidator(schema)
    sanitized, errors = validator.validate({})
    assert "missing and required" in errors[0]
    assert sanitized["a"] is None

def test_strict_mode_raises():
    schema = [Field("a", int)]
    validator = SchemaValidator(schema, strict_mode=True)
    with pytest.raises(ValidationError):
        validator.validate({})

def test_aliases():
    schema = [Field("temp_c", float, aliases=["temp", "temperature_C"])]
    validator = SchemaValidator(schema)
    data = {"temp": "36.6"}
    sanitized, errors = validator.validate(data)
    assert sanitized["temp_c"] == 36.6
    assert not errors

def test_custom_validator():
    def positive(x):
        if x is None or x < 0:
            raise ValueError("must be >=0")
    schema = [Field("x", int, validators=[positive])]
    validator = SchemaValidator(schema)
    _, errors = validator.validate({"x": "-5"})
    assert "must be >=0" in errors[0]

def test_unknown_fields_ignored(caplog):
    schema = [Field("a", int)]
    validator = SchemaValidator(schema)
    caplog.set_level("DEBUG")
    sanitized, errors = validator.validate({"a": 1, "z": 9})
    assert "Ignoring unknown field 'z'" in caplog.text

def test_json_schema_generation():
    schema = [
        Field("a", int),
        Field("b", str, aliases=["beta"], optional=True)
    ]
    validator = SchemaValidator(schema)
    js = validator.to_json_schema()
    assert js["type"] == "object"
    assert set(js["properties"].keys()) == {"a", "b"}
    assert "required" in js and "a" in js["required"]

def test_sample_generation():
    schema = [
        Field("i", int),
        Field("f", float),
        Field("s", str, optional=True),
        Field("b", bool)
    ]
    validator = SchemaValidator(schema)
    samples = validator.sample(5)
    assert len(samples) == 5
    for rec in samples:
        assert "i" in rec and isinstance(rec["i"], int)
        assert "f" in rec and isinstance(rec["f"], float)
        assert "b" in rec and isinstance(rec["b"], bool)
        assert "s" in rec

