import os
import tempfile
import threading
import time
import pytest
import yaml
import toml
from config_toolkit import (
    toolkit,
    resolve_variables,
    load_toml,
    load_yaml,
    register_coercer,
    register_hook,
    merge_lists,
    set_profile,
    get,
    with_defaults,
    watch_and_reload,
    ConfigToolkit,
)

def test_load_toml_and_yaml(tmp_path):
    # Create TOML file
    toml_content = {"service": {"port": 8080, "name": "api"}}
    toml_file = tmp_path / "config.toml"
    toml_file.write_text(toml.dumps(toml_content))
    loaded_toml = load_toml(str(toml_file))
    assert loaded_toml == toml_content

    # Create YAML file
    yaml_content = {"db": {"user": "admin", "pass": "secret"}}
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml.safe_dump(yaml_content))
    loaded_yaml = load_yaml(str(yaml_file))
    assert loaded_yaml == yaml_content

def test_merge_lists_unique():
    global_list = [{"name": "g1"}, {"name": "g2"}]
    tenant_list = [{"name": "t1"}, {"name": "g2"}]
    merged = merge_lists(global_list, tenant_list)
    # should keep g1, g2 then t1 (g2 duplicate ignored)
    assert merged == [{"name": "g1"}, {"name": "g2"}, {"name": "t1"}]

def test_set_profile_valid_and_invalid():
    set_profile("enterprise")
    assert toolkit.profile == "enterprise"
    set_profile("standard")
    assert toolkit.profile == "standard"
    with pytest.raises(ValueError):
        set_profile("invalid_profile")

def test_register_coercer_and_hook():
    # Clear existing
    toolkit.coercers.clear()
    toolkit.hooks = {"pre_merge": [], "post_merge": [], "export": []}

    def dummy_coercer(x): return f"coerced-{x}"
    register_coercer("TypeA", dummy_coercer)
    assert "TypeA" in toolkit.coercers
    assert toolkit.coercers["TypeA"](10) == "coerced-10"

    def pre_hook(cfg): cfg["hooked"] = True
    def post_hook(cfg): cfg["post"] = True
    def export_hook(cfg): cfg["exported"] = True

    register_hook("pre_merge", pre_hook)
    register_hook("post_merge", post_hook)
    register_hook("export", export_hook)

    assert pre_hook in toolkit.hooks["pre_merge"]
    assert post_hook in toolkit.hooks["post_merge"]
    assert export_hook in toolkit.hooks["export"]

    with pytest.raises(ValueError):
        register_hook("unknown_phase", lambda x: x)

def test_resolve_variables_and_get():
    os.environ["ENV_VAR"] = "env123"
    config = {
        "global": {"rate": {"limit": 50}},
        "service": {"password": "${global.rate.limit}", "mode": "${ENV_VAR}"},
        "plain": "no change",
    }
    resolved = resolve_variables(config)
    assert resolved["service"]["password"] == "50"
    assert resolved["service"]["mode"] == "env123"
    assert resolved["plain"] == "no change"

    # Test get with stored data
    toolkit.data = {"a": {"b": {"c": 42}}}
    assert get("a.b.c") == 42

def test_with_defaults():
    config = {"a": 1, "nested": {"x": True}}
    defaults = {"b": 2, "nested": {"x": False, "y": False}}
    merged = with_defaults(config, defaults)
    # 'a' stays, 'b' added, nested.x stays True, nested.y added
    assert merged["a"] == 1
    assert merged["b"] == 2
    assert merged["nested"]["x"] is True
    assert merged["nested"]["y"] is False

def test_watch_and_reload_calls_callback():
    called = {"count": 0}
    def cb():
        called["count"] += 1
    watch_and_reload(["/path"], cb)
    assert called["count"] == 1

def test_independent_toolkit_instances():
    # Ensure multiple instances don't share state
    t1 = ConfigToolkit()
    t2 = ConfigToolkit()
    assert t1 is not t2
    t1.data["key"] = "value1"
    t2.data["key"] = "value2"
    assert t1.data["key"] == "value1"
    assert t2.data["key"] == "value2"
