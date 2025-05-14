import os
import pytest
from config_framework.core import (
    expand_env_vars,
    set_env_expander,
    report_error,
    ConfigError,
)

def test_env_expand_default(monkeypatch):
    monkeypatch.setenv("X", "Y")
    assert expand_env_vars("$X") == "Y"

def test_env_expand_override():
    def exp(v):
        return v.upper()
    set_env_expander(exp)
    assert expand_env_vars("test") == "TEST"

def test_report_error_raises_ConfigError():
    with pytest.raises(ConfigError) as exc:
        report_error("fail", {"k": "v"})
    assert "fail" in str(exc.value)
    assert exc.value.info == {"k": "v"}
