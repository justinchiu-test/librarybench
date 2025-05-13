import pytest
from validator import Validator, ValidationError
from example_async import tax_id_lookup
import plugins

# Sample schema covering all requirements
sample_schema = {
    "properties": {
        "status": {"type": "string", "enum": ["pending", "approved", "rejected"], "required": True},
        "coupon_applied": {"type": "boolean", "required": True},
        "discount_code": {
            "type": "string",
            "nullable": True,
            "conditional": {
                "if": {"coupon_applied": True},
                "then": {"type": "string", "pattern": r"^DISCOUNT[0-9]{2}$"}
            }
        },
        "region": {"type": "string", "default": {"default": "US", "fr-FR": "FR"}},
        "inventory_level": {"type": "integer", "minimum": 0, "maximum": 1000},
        "response_time": {"type": "number", "maximum": 5000},
        "file_size": {"type": "integer", "maximum": 1048576},
        "tax_id": {"type": "string", "async": {"func": tax_id_lookup, "timeout": 0.1}},
        "notes": {"type": "string", "nullable": True},
        "attachments": {"type": "array", "nullable": True},
    }
}

def test_enum_constraints_valid():
    v = Validator(sample_schema)
    data = {"status": "approved", "coupon_applied": False, "inventory_level": 0,
            "response_time": 100, "file_size": 1000, "tax_id": "TX123"}
    errs = v.validate(data)
    assert errs == []

def test_enum_constraints_invalid():
    v = Validator(sample_schema)
    data = {"status": "unknown", "coupon_applied": False, "inventory_level": 0,
            "response_time": 100, "file_size": 1000, "tax_id": "TX123"}
    errs = v.validate(data)
    assert ValidationError("status", "Value 'unknown' not in enum ['pending', 'approved', 'rejected']") in errs

def test_conditional_validation_applied():
    v = Validator(sample_schema)
    data = {"status": "pending", "coupon_applied": True, "discount_code": "DISCOUNT10",
            "inventory_level": 10, "response_time": 10, "file_size": 10, "tax_id": "TX1"}
    errs = v.validate(data)
    assert errs == []

def test_conditional_validation_missing():
    v = Validator(sample_schema)
    data = {"status": "pending", "coupon_applied": True, "discount_code": None,
            "inventory_level": 10, "response_time": 10, "file_size": 10, "tax_id": "TX1"}
    errs = v.validate(data)
    # None is allowed as nullable but pattern should not apply when None
    assert errs == []

def test_conditional_validation_pattern_fail():
    v = Validator(sample_schema)
    data = {"status": "pending", "coupon_applied": True, "discount_code": "BAD",
            "inventory_level": 10, "response_time": 10, "file_size": 10, "tax_id": "TX1"}
    errs = v.validate(data)
    assert ValidationError("discount_code", "Conditional: Pattern mismatch") in errs

def test_default_values_locale_default():
    v = Validator(sample_schema)
    data = {"status": "pending", "coupon_applied": False,
            "inventory_level": 0, "response_time": 0, "file_size": 0, "tax_id": "TX0"}
    errs = v.validate(data, context={"locale": "fr-FR"})
    assert errs == []
    assert data["region"] == "FR"

def test_default_values_global_default():
    v = Validator(sample_schema)
    data = {"status": "pending", "coupon_applied": False,
            "inventory_level": 0, "response_time": 0, "file_size": 0, "tax_id": "TX0"}
    errs = v.validate(data)
    assert errs == []
    assert data["region"] == "US"

def test_range_checks_invalid():
    v = Validator(sample_schema)
    data = {"status": "pending", "coupon_applied": False,
            "inventory_level": -1, "response_time": 6000, "file_size": 2000000, "tax_id": "TX0"}
    errs = v.validate(data)
    assert ValidationError("inventory_level", "Value -1 below minimum 0") in errs
    assert ValidationError("response_time", "Value 6000 above maximum 5000") in errs
    assert ValidationError("file_size", "Value 2000000 above maximum 1048576") in errs

def test_optional_fields():
    v = Validator(sample_schema)
    # omitted
    data1 = {"status": "pending", "coupon_applied": False,
             "inventory_level": 0, "response_time": 0, "file_size": 0, "tax_id": "TX0"}
    errs1 = v.validate(data1)
    assert errs1 == []
    # null
    data2 = dict(data1, notes=None, attachments=None)
    errs2 = v.validate(data2)
    assert errs2 == []
    # wrong type
    data3 = dict(data1, notes=123, attachments="notalist")
    errs3 = v.validate(data3)
    assert ValidationError("notes", "Expected string") in errs3
    assert ValidationError("attachments", "Expected array") in errs3

def test_async_validation_success_and_fail_and_timeout():
    v = Validator(sample_schema)
    base = {"status": "pending", "coupon_applied": False,
            "inventory_level": 0, "response_time": 0, "file_size": 0}
    # success
    data_s = dict(base, tax_id="TX999")
    errs_s = v.validate(data_s)
    assert all(e.path != "tax_id" for e in errs_s)
    # fail (invalid)
    data_f = dict(base, tax_id="XX999")
    errs_f = v.validate(data_f)
    assert ValidationError("tax_id", "Async validation failed") in errs_f
    # timeout
    data_t = dict(base, tax_id="timeout")
    errs_t = v.validate(data_t)
    assert ValidationError("tax_id", "Async validation timeout") in errs_t

def test_single_item_validation():
    v = Validator(sample_schema)
    data_list = [
        {"status": "pending", "coupon_applied": False,
         "inventory_level": 0, "response_time": 0, "file_size": 0, "tax_id": "TX1"},
        ["bad"],
    ]
    # without single_item
    errs = v.validate(data_list, single_item=False)
    assert ValidationError("", "Expected object, got list") in errs
    # with single_item
    errs_si = v.validate(data_list, single_item=True)
    assert ValidationError("[1]", "Expected object, got list") in errs_si

def test_strict_mode():
    v = Validator(sample_schema, strict=False)
    data = {"status": "pending", "coupon_applied": False,
            "inventory_level": 0, "response_time": 0, "file_size": 0, "tax_id": "TX0", "extra": 1}
    errs = v.validate(data)
    assert all(e.path != "extra" for e in errs)
    v_strict = Validator(sample_schema, strict=True)
    errs2 = v_strict.validate(data)
    assert ValidationError("extra", "Unexpected field") in errs2

def test_plugin_system():
    v = Validator(sample_schema, plugins=[plugins.no_pii])
    data = {"status": "pending", "coupon_applied": False,
            "inventory_level": 0, "response_time": 0, "file_size": 0, "tax_id": "TX0", "name": "Alice"}
    errs = v.validate(data)
    assert ValidationError("name", "PII not allowed") in errs
