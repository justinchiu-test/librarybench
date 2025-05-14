import pytest
from rate_limiter.config import validate_config

def test_validate_config_success():
    cfg = {"name": "test", "rate": 5, "capacity": 10}
    assert validate_config(cfg) is True

def test_validate_config_missing_field():
    with pytest.raises(ValueError):
        validate_config({"name": "x", "rate": 5})

def test_validate_config_bad_types():
    with pytest.raises(ValueError):
        validate_config({"name": 123, "rate": -1, "capacity": 0})
