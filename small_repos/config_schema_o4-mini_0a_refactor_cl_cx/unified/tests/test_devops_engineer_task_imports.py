import pytest
import configschema as config_manager

def test_module_importable():
    # basic import test
    assert hasattr(config_manager, 'load_config')
    assert hasattr(config_manager, 'ConfigManager')
    assert hasattr(config_manager, 'expand_env_vars')
    assert hasattr(config_manager, 'with_config')
