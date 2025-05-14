import pytest
from config_manager.plugin import register_plugin, get_plugins

def dummy_loader(x):
    return x

def test_register_and_get_plugins():
    # register loader
    register_plugin(loaders=dummy_loader)
    loaders = get_plugins('loaders')
    assert dummy_loader in loaders

def test_register_invalid_hook():
    with pytest.raises(ValueError):
        register_plugin(badhook=lambda x: x)
