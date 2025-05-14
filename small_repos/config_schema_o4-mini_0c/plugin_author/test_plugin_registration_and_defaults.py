import pytest
from config_framework.core import (
    register_plugin,
    PLUGINS,
    set_default_factory,
    get_default,
)

def test_register_multiple_plugins_and_defaults():
    state = {}
    def init1():
        state['p1'] = True
    def init2():
        state['p2'] = True
    register_plugin("p1", init1)
    register_plugin("p2", init2)
    assert "p1" in PLUGINS and "p2" in PLUGINS
    assert state['p1'] and state['p2']
    set_default_factory("a", lambda: 1)
    set_default_factory("b", lambda: 2)
    assert get_default("a") == 1
    assert get_default("b") == 2
    assert get_default("c") is None
