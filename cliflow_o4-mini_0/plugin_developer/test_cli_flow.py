import os
import tempfile
import pytest

import cli_flow
import json
yaml = cli_flow.yaml

from cli_flow import (
    generate_completion, export_workflow_docs, discover_plugins,
    redirect_io, use_profile, serialize_data, check_version,
    manage_marketplace, HookManager, run_tests
)

def test_generate_completion():
    cmds = ["start", "stop"]
    comp = generate_completion(cmds)
    assert "start" in comp and comp["start"] == ["start_opt1", "start_opt2"]
    assert "stop" in comp and comp["stop"] == ["stop_opt1", "stop_opt2"]

def test_export_workflow_docs():
    steps = ["init", "build", "deploy"]
    doc = export_workflow_docs(steps)
    expected = "Workflow Documentation:\n- init\n- build\n- deploy"
    assert doc == expected

def test_discover_plugins(tmp_path):
    # create fake plugin files
    files = ["a.py", "b.py", "__init__.py", "readme.txt"]
    for f in files:
        (tmp_path / f).write_text("")
    found = discover_plugins(str(tmp_path))
    assert set(found) == {"a", "b"}

def test_redirect_io():
    test_input = "hello"
    with redirect_io(test_input) as (stdin, stdout):
        data = input()
        print("world")
    assert data == "hello"
    out = stdout.getvalue().strip()
    assert out == "world"

def test_use_profile():
    profiles = {"dev": {"url": "localhost"}, "prod": {"url": "example.com"}}
    assert use_profile("dev", profiles) == {"url": "localhost"}
    with pytest.raises(KeyError):
        use_profile("staging", profiles)

def test_serialize_json(tmp_path):
    data = {"a": 1}
    s = serialize_data(data, "json")
    assert s == '{"a": 1}'
    p = tmp_path / "out.json"
    ret = serialize_data(data, "json", str(p))
    assert ret == str(p)
    assert json.loads(p.read_text()) == data

def test_serialize_csv(tmp_path):
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    s = serialize_data(data, "csv")
    lines = s.strip().splitlines()
    assert lines[0] == "a,b"
    assert lines[1] == "1,2"
    p = tmp_path / "out.csv"
    ret = serialize_data(data, "csv", str(p))
    assert ret == str(p)
    assert (tmp_path / "out.csv").read_text().strip().splitlines()[1] == "1,2"

def test_serialize_yaml(tmp_path):
    if yaml is None:
        pytest.skip("PyYAML not installed")
    data = {"x": [1, 2]}
    s = serialize_data(data, "yaml")
    assert "x:" in s
    p = tmp_path / "out.yaml"
    ret = serialize_data(data, "yaml", str(p))
    assert ret == str(p)
    assert "x:" in p.read_text()

def test_check_version():
    assert check_version("1.0.0", "1.2.0")
    assert check_version("1.2.0", "1.2.0")
    with pytest.raises(Exception):
        check_version("2.0.0", "1.2.0")

def test_manage_marketplace():
    mp = {}
    assert manage_marketplace("publish", "p1", "0.1.0", mp)
    assert mp["p1"] == "0.1.0"
    with pytest.raises(ValueError):
        manage_marketplace("publish", "p1", "0.1.0", mp)
    assert manage_marketplace("update", "p1", "0.2.0", mp)
    assert mp["p1"] == "0.2.0"
    with pytest.raises(ValueError):
        manage_marketplace("update", "p2", "0.1.0", mp)
    with pytest.raises(ValueError):
        manage_marketplace("delete", "p1", "0.1.0", mp)

def test_hook_manager():
    hm = HookManager()
    hm.register("pre", lambda x: x + 1)
    hm.register("post", lambda x: x * 2)
    assert hm.run_hooks("pre", 5) == [6]
    assert hm.run_hooks("post", 5) == [10]
    with pytest.raises(ValueError):
        hm.register("unknown", lambda: None)
    with pytest.raises(ValueError):
        hm.run_hooks("unknown")

def test_run_tests():
    assert run_tests() == "Test harness invoked"
