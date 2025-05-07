import pytest
from DevOps_Engineer.devops_utils.integration import integration_tests

def test_integration_tests_returns_dict():
    result = integration_tests()
    assert isinstance(result, dict)

def test_integration_tests_keys_and_values():
    expected_keys = {'database', 'cache', 'message_queue'}
    result = integration_tests()
    assert set(result.keys()) == expected_keys
    for val in result.values():
        assert isinstance(val, bool)
        assert val is True
