import pytest
from Data_Engineer.workflow.auth import authenticate, USER_TOKENS

def test_auth_success():
    token = list(USER_TOKENS.values())[0]
    @authenticate(token)
    def secured():
        return "ok"
    assert secured() == "ok"

def test_auth_failure():
    @authenticate("invalid")
    def secured():
        return "ok"
    with pytest.raises(PermissionError):
        secured()
