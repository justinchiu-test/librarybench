import os
import json
import configparser
import tempfile
import ipaddress
import pytest
from cli_toolkit import (
    load_config, run_dry_run, branch_flow, prompt_interactive,
    secure_prompt, retry, Context, export_docs, register_hook,
    run_hooks, validate_params
)

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def test_load_config_json(tmp_path):
    data = {"key": "value", "num": 1}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(data))
    result = load_config(str(p))
    assert result == data

def test_load_config_yaml(tmp_path):
    yaml_content = "key: value\nlist:\n  - a\n  - b\n"
    p = tmp_path / "config.yaml"
    p.write_text(yaml_content)
    result = load_config(str(p))
    assert result["key"] == "value"
    assert result["list"] == ["a", "b"]

def test_load_config_toml(tmp_path):
    toml_content = 'key = "value"\nnumber = 5\n'
    p = tmp_path / "config.toml"
    p.write_text(toml_content)
    result = load_config(str(p))
    assert result["key"] == "value"
    assert result["number"] == 5

def test_load_config_ini(tmp_path):
    ini = "[section]\nkey = value\nnum = 2\n"
    p = tmp_path / "config.ini"
    p.write_text(ini)
    result = load_config(str(p))
    assert "section" in result
    assert result["section"]["key"] == "value"
    assert result["section"]["num"] == "2"

def test_load_config_unsupported(tmp_path):
    p = tmp_path / "config.txt"
    p.write_text("data")
    with pytest.raises(ValueError):
        load_config(str(p))

def test_run_dry_run():
    cmds = ["echo hi", "ping"]
    hosts = ["host1", "host2"]
    preview = run_dry_run(cmds, hosts)
    expected = [
        ("host1", "echo hi"), ("host1", "ping"),
        ("host2", "echo hi"), ("host2", "ping"),
    ]
    assert preview == expected

def test_branch_flow_matching_and_default():
    called = []
    def high(): 
        called.append("high")
        return "H"
    def low():
        called.append("low")
        return "L"
    res = branch_flow(1, {1: high, 'default': low})
    assert res == "H"
    called.clear()
    res2 = branch_flow(2, {1: high, 'default': low})
    assert res2 == "L"
    with pytest.raises(KeyError):
        branch_flow(3, {1: high})

def test_prompt_interactive(monkeypatch):
    inputs = iter(["bad", "yes"])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    ans = prompt_interactive("Confirm", choices=["yes", "no"])
    assert ans == "yes"
    # without choices
    inputs2 = iter(["anything"])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs2))
    ans2 = prompt_interactive("Enter")
    assert ans2 == "anything"

def test_secure_prompt(monkeypatch):
    monkeypatch.setattr('getpass.getpass', lambda prompt: "secret_pwd")
    pwd = secure_prompt("Enter pwd: ")
    assert pwd == "secret_pwd"

def test_retry_success_after_failures():
    calls = {'count': 0}
    @retry(retries=2, exceptions=(ValueError,), backoff=0)
    def flaky():
        calls['count'] += 1
        if calls['count'] < 3:
            raise ValueError("fail")
        return "ok"
    assert flaky() == "ok"
    assert calls['count'] == 3

def test_retry_exhausted():
    @retry(retries=1, exceptions=(ValueError,), backoff=0)
    def always_fail():
        raise ValueError("nope")
    with pytest.raises(ValueError):
        always_fail()

def test_context_and_export_docs_md():
    ctx = Context()
    ctx.add_host("h1")
    ctx.add_host("h2")
    ctx.add_result("res1")
    ctx.update_compliance("pol1", "pass")
    md = export_docs(ctx, fmt='md')
    assert "# Audit Report" in md
    assert "- h1" in md and "- h2" in md
    assert "- res1" in md
    assert "- pol1: pass" in md

def test_export_docs_html():
    ctx = Context()
    ctx.add_host("hA")
    ctx.add_result("rA")
    ctx.update_compliance("p", "ok")
    html = export_docs(ctx, fmt='html')
    assert "<h1>Audit Report</h1>" in html
    assert "<li>hA</li>" in html
    assert "<li>rA</li>" in html
    assert "<li>p: ok</li>" in html
    with pytest.raises(ValueError):
        export_docs(ctx, fmt='txt')

def test_hooks():
    calls = []
    def pre(x):
        calls.append(f"pre:{x}")
    def post(x):
        calls.append(f"post:{x}")
    register_hook('pre_scan', pre)
    register_hook('post_scan', post)
    run_hooks('pre_scan', 'A')
    run_hooks('post_scan', 'B')
    assert calls == ["pre:A", "post:B"]

def test_validate_params_success():
    assert validate_params(targets=["127.0.0.1", "10.0.0.1"], severity=5, policy_ids=["p1", "p2"])

def test_validate_params_invalid_ip():
    with pytest.raises(ValueError):
        validate_params(targets=["not_an_ip"])

def test_validate_params_invalid_severity():
    with pytest.raises(ValueError):
        validate_params(severity=20)

def test_validate_params_invalid_policy():
    with pytest.raises(ValueError):
        validate_params(policy_ids=[123, ""])
