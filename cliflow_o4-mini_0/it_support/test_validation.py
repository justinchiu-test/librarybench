import pytest
from onboarding.validation import validate_username, validate_department, validate_license_key, validate_params

def test_validate_username_ok():
    assert validate_username("user123")

def test_validate_username_fail():
    with pytest.raises(ValueError):
        validate_username("user!23")

def test_validate_department_ok():
    assert validate_department("IT")
    assert validate_department("HRDE")

def test_validate_department_fail():
    with pytest.raises(ValueError):
        validate_department("it")
    with pytest.raises(ValueError):
        validate_department("A")

def test_validate_license_key_ok():
    assert validate_license_key("ABCD-1234-EFGH-5678")

def test_validate_license_key_fail():
    with pytest.raises(ValueError):
        validate_license_key("1234-5678")

def test_validate_params_all():
    assert validate_params("user", "DEPT", "ABCD-1234-EFGH-5678")
