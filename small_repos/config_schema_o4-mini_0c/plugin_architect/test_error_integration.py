import pytest
from config_manager.errors import report_error

def some_validator(key, val):
    if not isinstance(val, int):
        msg = report_error("f", 1, "s", key, "int", type(val).__name__, suggestion="make it int")
        raise ValueError(msg)

def test_validator_raises():
    with pytest.raises(ValueError) as e:
        some_validator("x", "bad")
    assert "expected int" in str(e.value)
