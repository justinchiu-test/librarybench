import pytest
from datavalidation.error_codes import ErrorCodeSupport

def test_get_known_code():
    ecs = ErrorCodeSupport()
    assert ecs.get_error_code('missing_field') == 100

def test_get_unknown_code():
    ecs = ErrorCodeSupport()
    assert ecs.get_error_code('no_such') == -1
