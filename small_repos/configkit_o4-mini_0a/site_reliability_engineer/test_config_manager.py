import os
import tempfile
import pytest
from srectl.config import ConfigManager

def test_config_manager_end_to_end(tmp_path, monkeypatch):
    # Create TOML config
    toml_path = tmp_path / "config.toml"
    toml_content = """
[alert]
threshold = "0.5"

[circuit_breaker]
error_rate = "40%"
"""
    toml_path.write_text(toml_content)
    # Env override
    monkeypatch.setenv('SRE_ALERT_THRESHOLD', '60%')
    # Argv override
    argv = ['--service.timeout', '20']
    cm = ConfigManager(str(toml_path), argv=argv)
    cfg = cm.config
    # Assert thresholds applied and coerced
    assert isinstance(cfg['alert']['threshold'], float)
    assert cfg['alert']['threshold'] == 0.6  # env override
    assert cfg['circuit_breaker']['error_rate'] == 0.4
    assert cfg['service']['timeout'] == 20
    # Test watcher on change
    events = {}
    def on_change(old=None, new=None):
        events['old'] = old
        events['new'] = new
    cm.on('alert.threshold_changed', on_change)
    # Modify TOML to new threshold
    toml_path.write_text("""
[alert]
threshold = "0.2"
""")
    # Simulate file change
    cm.simulate_file_change(str(toml_path))
    assert events['old'] == 0.6
    assert events['new'] == 0.2
