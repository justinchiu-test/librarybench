import pytest
import chaoslib

def test_assert_request_body_validator_fails():
    req = {'body': 'invalid'}
    validator = lambda b: b == 'valid'
    with pytest.raises(AssertionError):
        chaoslib.assertRequestBody(validator, req)

def test_assert_request_body_validator_passes():
    req = {'body': 'valid'}
    validator = lambda b: b == 'valid'
    chaoslib.assertRequestBody(validator, req)
