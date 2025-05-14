import os
import pytest
from retry_engine.config import EnvVarOverrides

def test_env_var_overrides(monkeypatch):
    env = {
        'RETRY_MAX_ATTEMPTS': '5',
        'RETRY_BASE_DELAY': '0.5',
        'RETRY_MAX_DELAY': '2.5',
        'RETRY_BACKOFF_STRATEGY': 'full_jitter',
        'CB_FAILURE_THRESHOLD': '4',
        'CB_RECOVERY_TIMEOUT': '120'
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    cfg = EnvVarOverrides()
    assert cfg.max_attempts == 5
    assert cfg.base_delay == 0.5
    assert cfg.max_delay == 2.5
    assert cfg.backoff_strategy == 'full_jitter'
    assert cfg.failure_threshold == 4
    assert cfg.recovery_timeout == 120
