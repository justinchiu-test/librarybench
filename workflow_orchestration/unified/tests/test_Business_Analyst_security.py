import pytest
from automation.security import SecurityManager, PermissionError, User

def test_add_and_authenticate_user():
    sm = SecurityManager()
    sm.add_user("alice", roles=["admin"])
    with pytest.raises(ValueError):
        sm.add_user("alice")
    sm.authenticate("alice")
    assert sm.current_user.username == "alice"
    assert "admin" in sm.current_user.roles

def test_check_permission_success_and_failure():
    sm = SecurityManager()
    sm.add_user("bob", roles=["user"])
    sm.authenticate("bob")
    # has role
    sm.check_permission("user")
    # missing role
    with pytest.raises(PermissionError):
        sm.check_permission("admin")
