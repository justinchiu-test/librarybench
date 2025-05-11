import os
import json
import platform_architect.toml as tomllib
import tempfile
import pytest
from platform_architect.config_manager import ConfigManager

def test_register_plugin_and_alert():
    mgr = ConfigManager()
    calls = []
    def alert_hook(entry):
        calls.append(entry["event"])
    mgr.register_plugin("alert", "test_alert", alert_hook)
    assert "test_alert" in mgr.plugins["alert"]
    mgr.log_event("custom_event", {"foo": "bar"})
    assert "custom_event" in calls

def test_validate_config_success_and_failure():
    cfg = {"a": 1, "b": {"c": "s"}}
    mgr = ConfigManager(initial_config=cfg)
    schema = {"a": int, "b": {"c": str}}
    assert mgr.validate_config(schema) is True
    bad_schema = {"a": str}
    with pytest.raises(TypeError):
        mgr.validate_config(bad_schema)
    missing_schema = {"x": int}
    with pytest.raises(ValueError):
        mgr.validate_config(missing_schema)

def test_export_to_env(tmp_path, monkeypatch):
    cfg = {"x": 10, "nested": {"y": "z"}}
    mgr = ConfigManager(initial_config=cfg)
    pairs = mgr.export_to_env()
    assert "X=10" in pairs
    assert "NESTED_Y=z" in pairs
    monkeypatch.delenv("X", raising=False)
    pairs2 = mgr.export_to_env(update_os_env=True)
    assert os.environ["X"] == "10"

def test_get_namespace_and_diff():
    cfg = {"auth": {"oauth": {"token": "abc"}}, "k": 1}
    mgr = ConfigManager(initial_config=cfg)
    ns = mgr.get_namespace("auth.oauth")
    assert ns == {"token": "abc"}
    # diff
    old = {"a": 1, "b": {"x": 2}}
    new = {"a": 1, "b": {"x": 3}, "c": 5}
    diff = mgr.diff_changes(old, new)
    assert "c" in diff["added"]
    assert "b.x" in diff["changed"]
    assert diff["changed"]["b.x"]["old"] == 2
    assert diff["changed"]["b.x"]["new"] == 3

def test_snapshot_and_events():
    mgr = ConfigManager()
    mgr.override_config("a", 5)
    snap = mgr.snapshots[-1]
    assert snap["config"]["a"] == 5
    assert any(e["event"] == "snapshot" for e in mgr.events)

def test_load_json_and_toml_sources(tmp_path):
    data_json = {"j": 1}
    json_file = tmp_path / "c.json"
    json_file.write_text(json.dumps(data_json))
    data_toml = {"t": {"k": "v"}}
    toml_file = tmp_path / "c.toml"
    import platform_architect.toml as toml as _toml
    toml_file.write_text(_toml.dumps(data_toml))
    mgr = ConfigManager()
    mgr.load_json_source(str(json_file))
    assert mgr.config["j"] == 1
    mgr.load_toml_source(str(toml_file))
    assert mgr.config["t"]["k"] == "v"
    # events and snapshots
    assert any(e["event"] == "config_loaded" for e in mgr.events)
    assert any(s["config"] == mgr.config for s in mgr.snapshots)

def test_load_env_source(monkeypatch):
    monkeypatch.setenv("PRE_A", "alpha")
    monkeypatch.setenv("PRE_B", "beta")
    mgr = ConfigManager()
    mgr.load_env_source(prefix="PRE_")
    assert mgr.config["A"] == "alpha"
    assert mgr.config["B"] == "beta"

def test_override_config_and_versioning():
    mgr = ConfigManager(initial_config={"x": 1})
    mgr.override_config("x", 2)
    assert mgr.config["x"] == 2
    assert any(e["event"] == "override" for e in mgr.events)
    prev_version = mgr.snapshots[-1]["version"]
    mgr.override_config("y.z", True)
    assert mgr.config["y"]["z"] is True
    assert mgr.snapshots[-1]["version"] > prev_version

def test_parse_cli_args():
    mgr = ConfigManager(initial_config={"a": 0})
    args = ["--a=10", "--new.key=true", "--ignore"]
    mgr.parse_cli_args(args)
    assert mgr.config["a"] == 10
    assert mgr.config["new"]["key"] is True

def test_plugin_loader_effect(tmp_path):
    mgr = ConfigManager()
    # loader plugin that multiplies all numeric values by 2
    def loader_hook(data):
        for k, v in data.items():
            if isinstance(v, int):
                data[k] = v * 2
        return data
    mgr.register_plugin("loader", "double_nums", loader_hook)
    # prepare json
    data = {"n": 3}
    f = tmp_path / "d.json"
    f.write_text(json.dumps(data))
    mgr.load_json_source(str(f))
    assert mgr.config["n"] == 6

def test_cli_parse_error_logged():
    mgr = ConfigManager()
    # malformed arg
    mgr.parse_cli_args(["--badarg"])
    assert any(e["event"] in ("cli_parse_error",) for e in mgr.events)
