import pytest
from retry_toolkit.config_support import ConfigFileSupport

def test_load_config(tmp_path):
    config_content = """
[retry]
max_attempts = 5
delay = 2.5

[backoff]
strategy = "expo"
"""
    path = tmp_path / "config.toml"
    path.write_text(config_content)
    cfg = ConfigFileSupport(str(path))
    assert cfg.get_retry_setting('max_attempts') == 5
    assert cfg.get_retry_setting('delay') == 2.5
    assert cfg.get_backoff_setting('strategy') == 'expo'
    assert cfg.get_retry_setting('nonexistent', 'default') == 'default'
