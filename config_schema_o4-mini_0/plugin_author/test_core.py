import os
import tempfile
import pytest
import config_framework.core as core
from config_framework.core import (
    define_validation_contexts,
    VALIDATION_CONTEXTS,
    register_converter,
    register_validator,
    validate_types,
    register_loader,
    load_config,
    merge_configs,
    report_error,
    ConfigError,
    register_plugin,
    PLUGINS,
    expand_env_vars,
    set_env_expander,
    add_cross_field_validator,
    run_cross_field_validators,
    set_default_factory,
    get_default,
)

def test_define_validation_contexts():
    assert "graphql-schema-check" not in VALIDATION_CONTEXTS
    define_validation_contexts("graphql-schema-check")
    assert "graphql-schema-check" in VALIDATION_CONTEXTS

def test_register_and_validate_converter_and_validator():
    register_converter("to_int", lambda v: int(v))
    def positive_validator(v):
        if v <= 0:
            raise ValueError("Value must be positive")
    register_validator("to_int", positive_validator)
    assert validate_types("to_int", "5") == 5
    with pytest.raises(ValueError):
        validate_types("to_int", "-3")

def test_register_and_load_config_tempfile():
    loader_called = {}
    def toml_loader(path):
        loader_called['path'] = path
        return {"parsed": "toml"}
    register_loader("toml", toml_loader)
    with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as tmp:
        tmp.write(b"dummy")
        tmp.flush()
        path = tmp.name
    result = load_config(path)
    assert loader_called['path'] == path
    assert result == {"parsed": "toml"}

def test_load_config_no_loader():
    with pytest.raises(ConfigError) as exc:
        load_config("no.such")
    assert "No loader for source" in str(exc.value)
    assert exc.value.info["source"] == "no.such"

def test_merge_configs_simple_and_nested():
    a = {"x": 1, "nested": {"a": 1}}
    b = {"y": 2, "nested": {"b": 2}}
    merged = merge_configs(a, b)
    assert merged["x"] == 1
    assert merged["y"] == 2
    assert merged["nested"]["a"] == 1
    assert merged["nested"]["b"] == 2

def test_report_error_custom_behavior():
    errors = {}
    def custom_report(message, info=None):
        errors['msg'] = message
        errors['info'] = info
        return "handled"
    original = core.ERROR_REPORTER
    core.ERROR_REPORTER = custom_report
    result = report_error("oops", {"foo": "bar"})
    assert result == "handled"
    assert errors['msg'] == "oops"
    assert errors['info'] == {"foo": "bar"}
    core.ERROR_REPORTER = original

def test_register_plugin():
    state = {}
    def initializer():
        state['inited'] = True
    register_plugin("test_plugin", initializer)
    assert "test_plugin" in PLUGINS
    assert state.get('inited') is True

def test_expand_env_vars_default_and_override(monkeypatch):
    monkeypatch.setenv("FOO", "bar")
    assert expand_env_vars("${FOO}") == "bar"
    def custom_expander(val):
        return val.replace("%FOO%", "baz")
    set_env_expander(custom_expander)
    assert expand_env_vars("value_%FOO%_end") == "value_baz_end"
    core.ENV_EXPANDER = core._default_env_expander

def test_cross_field_validator():
    def validator(cfg):
        if cfg.get("a") and "b" not in cfg:
            raise Exception("b is required when a is True")
    add_cross_field_validator("check_ab", validator)
    cfg1 = {"a": True, "b": 2}
    assert run_cross_field_validators(cfg1) == []
    cfg2 = {"a": True}
    errs = run_cross_field_validators(cfg2)
    assert errs == [("check_ab", "b is required when a is True")]

def test_set_default_factory_and_get_default():
    set_default_factory("now", lambda: "timestamp")
    assert get_default("now") == "timestamp"
    assert get_default("missing") is None
