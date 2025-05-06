import pytest
from it_manager.auth import AuthManager, AuthenticationError, AuthorizationError

def test_add_and_authenticate_user():
    AuthManager._users.clear()
    AuthManager._roles.clear()
    AuthManager._permissions.clear()

    AuthManager.add_user("alice", "password123")
    with pytest.raises(AuthenticationError):
        AuthManager.authenticate("alice", "wrong")
    assert AuthManager.authenticate("alice", "password123") is True

def test_permissions_and_roles():
    AuthManager._users.clear()
    AuthManager._roles.clear()
    AuthManager._permissions.clear()

    AuthManager.add_user("bob", "p")
    AuthManager.assign_role("bob", "admin")
    AuthManager.add_permission("admin", "deploy")
    # success
    assert AuthManager.authorize("bob", "deploy") is True
    # missing perm
    with pytest.raises(AuthorizationError):
        AuthManager.authorize("bob", "shutdown")

def test_requires_permission_decorator():
    AuthManager._users.clear()
    AuthManager._roles.clear()
    AuthManager._permissions.clear()

    AuthManager.add_user("carol", "pw")
    AuthManager.assign_role("carol", "operator")
    AuthManager.add_permission("operator", "run_task")

    @AuthManager.requires_permission("run_task")
    def do_task(x, username=None):
        return x * 2

    with pytest.raises(AuthorizationError):
        do_task(3, username="carol_wrong")
    assert do_task(4, username="carol") == 8
