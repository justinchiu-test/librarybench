import pytest
from workflow.auth import AuthManager, AuthError, requires_auth

class Dummy:
    def __init__(self):
        from workflow.auth import AuthManager
        self._auth_manager = AuthManager()
        self.called = False

    @requires_auth
    def protected(self, x):
        self.called = True
        return x * 2

def test_auth_manager():
    am = AuthManager()
    am.register_token('tok1')
    assert am.authenticate('tok1') is True
    with pytest.raises(AuthError):
        am.authenticate('bad')

def test_requires_auth_success():
    d = Dummy()
    d._auth_manager.register_token('good')
    res = d.protected(3, token='good')
    assert res == 6
    assert d.called

def test_requires_auth_failure():
    d = Dummy()
    with pytest.raises(AuthError):
        d.protected(2, token='nope')
    with pytest.raises(AuthError):
        d.protected(2)  # no token
