import pytest
from config_framework.core import (
    define_validation_contexts,
    VALIDATION_CONTEXTS,
    register_converter,
    register_validator,
    validate_types,
)

def test_multiple_validation_contexts():
    define_validation_contexts("ctx1", "ctx2", "ctx3")
    assert "ctx1" in VALIDATION_CONTEXTS
    assert "ctx2" in VALIDATION_CONTEXTS
    assert "ctx3" in VALIDATION_CONTEXTS

def test_type_conversion_and_validation_order():
    calls = []
    def conv(v):
        calls.append(f"conv:{v}")
        return v * 2
    def val(v):
        calls.append(f"val:{v}")
    register_converter("double", conv)
    register_validator("double", val)
    result = validate_types("double", 3)
    assert result == 6
    assert calls == ["conv:3", "val:6"]

def test_validate_without_converter():
    # validator only
    def val2(v):
        if v != "ok":
            raise ValueError("not ok")
    register_validator("check", val2)
    assert validate_types("check", "ok") == "ok"
    with pytest.raises(ValueError):
        validate_types("check", "bad")
