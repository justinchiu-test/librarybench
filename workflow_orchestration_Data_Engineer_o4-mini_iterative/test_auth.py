import pytest
from pipeline.auth import Auth, AuthError

def test_add_and_login_success():
    auth = Auth()
    auth.add_user('alice', 'secret', roles=['user'])
    token = auth.login('alice', 'secret')
    assert token == 'alice'

def test_login_invalid_credentials():
    auth = Auth()
    auth.add_user('bob', 'pwd', roles=['user'])
    with pytest.raises(AuthError):
        auth.login('bob', 'wrong')

def test_authorization_admin_vs_user():
    auth = Auth()
    auth.add_user('admin', 'adminpass', roles=['admin'])
    admin_token = auth.login('admin', 'adminpass')
    assert auth.authorize(admin_token, 'any_action')

    auth.add_user('charlie', 'charliepass', roles=['user'])
    user_token = auth.login('charlie', 'charliepass')
    assert auth.authorize(user_token, 'add_task')
    assert auth.authorize(user_token, 'run_scheduler')
    assert not auth.authorize(user_token, 'delete_task')
