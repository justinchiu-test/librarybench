import os
from plugin_framework.decorators import env_inject

def test_env_inject(monkeypatch):
    monkeypatch.setenv('FOO', 'bar')
    @env_inject
    def f(foo):
        return foo
    assert f() == 'bar'
