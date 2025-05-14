import pytest
import asyncio
from compliance.engine import ComplianceValidator, ComplianceError

@pytest.mark.parametrize("consent,has_timestamp", [
    ("granted", False),
    ("pending", False),
    ("revoked", True),
])
def test_conditional_deletion_timestamp(consent, has_timestamp):
    validator = ComplianceValidator(strict_mode=True)
    req = {
        "user_id": "user123",
        "age": 30,
        "data_retention_policy": "short_term",
        "user_consent_status": consent,
    }
    if has_timestamp:
        req["deletion_timestamp"] = "2023-01-01T00:00:00Z"
    if consent == "revoked":
        with pytest.raises(ComplianceError):
            validator.validate(req)
    else:
        res = validator.validate(req)
        assert res["policy_version"] == validator.DEFAULT_POLICY_VERSION

def test_enum_constraints():
    validator = ComplianceValidator(strict_mode=True)
    req = {
        "user_id": "u1",
        "age": 25,
        "data_retention_policy": "invalid",
        "user_consent_status": "granted",
    }
    with pytest.raises(ComplianceError):
        validator.validate(req)
    req["data_retention_policy"] = "long_term"
    req["user_consent_status"] = "invalid"
    with pytest.raises(ComplianceError):
        validator.validate(req)

def test_range_checks_retention():
    validator = ComplianceValidator(strict_mode=True)
    req = {
        "user_id": "u2",
        "age": 20,
        "data_retention_policy": "long_term",
        "user_consent_status": "granted",
        "retention_period": 10,
    }
    with pytest.raises(ComplianceError):
        validator.validate(req)
    req["retention_period"] = 100
    res = validator.validate(req)
    assert res["retention_period"] == 100

def test_minor_flag():
    validator = ComplianceValidator(strict_mode=True)
    req = {
        "user_id": "u3",
        "age": 15,
        "data_retention_policy": "short_term",
        "user_consent_status": "granted",
    }
    res = validator.validate(req)
    assert res["minor"] is True

def test_strict_unknown_field():
    validator = ComplianceValidator(strict_mode=True)
    req = {
        "user_id": "u4",
        "age": 40,
        "data_retention_policy": "short_term",
        "user_consent_status": "granted",
        "foo": "bar",
    }
    with pytest.raises(ComplianceError):
        validator.validate(req)

def test_permissive_unknown_field():
    validator = ComplianceValidator(strict_mode=False)
    req = {
        "user_id": "u5",
        "age": 40,
        "data_retention_policy": "short_term",
        "user_consent_status": "granted",
        "foo": "bar",
    }
    res = validator.validate(req)
    assert "foo" in res

@pytest.mark.asyncio
async def test_async_anonymization():
    validator = ComplianceValidator(strict_mode=True)
    req = {
        "user_id": "u6",
        "age": 30,
        "data_retention_policy": "short_term",
        "user_consent_status": "granted",
        "pii_fields": ["user_id"]
    }
    res = await validator._validate(req)
    assert res["user_id"] == "****"
