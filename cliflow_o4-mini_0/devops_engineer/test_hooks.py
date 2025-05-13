import pytest
from cli_framework.context import Context

def test_register_and_run_hooks():
    ctx = Context()
    called = []
    def on_exit(msg):
        called.append(msg)
    ctx.register_hook('on-exit', on_exit)
    ctx.run_hooks('on-exit', 'bye')
    assert called == ['bye']

def test_register_invalid():
    ctx = Context()
    with pytest.raises(ValueError):
        ctx.register_hook('invalid-event', lambda: None)
