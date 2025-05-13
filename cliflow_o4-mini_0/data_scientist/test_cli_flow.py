import os
import tempfile
import pytest
import configparser
import json
import getpass
from cli_flow import (
    load_config, run_dry_run, branch_flow, prompt_interactive,
    secure_prompt, retry, Context, export_docs, HookManager,
    validate_params
)

def test_load_config_json(tmp_path):
    data = {"a": 1, "b": "two"}
    p = tmp_path / "test.json"
    p.write_text(json.dumps(data))
    assert load_config(str(p)) == data

def test_load_config_yaml(tmp_path, monkeypatch):
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed")
    data = {"a": 1, "b": "two"}
    p = tmp_path / "test.yaml"
    p.write_text(yaml.safe_dump(data))
    assert load_config(str(p)) == data

def test_load_config_toml(tmp_path):
    try:
        import toml
    except ImportError:
        pytest.skip("toml not installed")
    data = {"a": 1, "b": "two"}
    p = tmp_path / "test.toml"
    p.write_text('a = 1\nb = "two"\n')
    assert load_config(str(p)) == data

def test_load_config_ini(tmp_path):
    parser = configparser.ConfigParser()
    parser['section1'] = {'a': '1', 'b': 'two'}
    p = tmp_path / "test.ini"
    with open(p, 'w') as f:
        parser.write(f)
    cfg = load_config(str(p))
    assert 'section1' in cfg
    assert cfg['section1']['a'] == '1'
    assert cfg['section1']['b'] == 'two'

def test_load_config_unsupported(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("nope")
    with pytest.raises(ValueError):
        load_config(str(p))

def test_run_dry_run():
    def step_one(): pass
    def step_two(): pass
    steps = ['init', step_one, step_two, 123]
    result = run_dry_run(steps)
    assert result == ['init', 'step_one', 'step_two', '123']

def test_branch_flow():
    called = []
    def success(ctx):
        called.append('success')
        return "ok"
    def failure(ctx):
        called.append('failure')
        return "fail"
    res1 = branch_flow(True, success, failure, {'x': 1})
    res2 = branch_flow(False, success, failure, {'x': 1})
    assert res1 == "ok"
    assert res2 == "fail"
    assert called == ['success', 'failure']

def test_prompt_interactive(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda prompt: "response")
    assert prompt_interactive("Prompt: ") == "response"

def test_secure_prompt(monkeypatch):
    monkeypatch.setattr(getpass, 'getpass', lambda prompt: "secret")
    assert secure_prompt("Password: ") == "secret"

def test_retry_success(monkeypatch):
    calls = {'count': 0}
    @retry(retries=3, exceptions=(ValueError,), delay=0.01, backoff=1)
    def flaky():
        if calls['count'] < 2:
            calls['count'] += 1
            raise ValueError("bad")
        return "good"
    assert flaky() == "good"
    assert calls['count'] == 2

def test_retry_fail():
    @retry(retries=2, exceptions=(ValueError,), delay=0, backoff=1)
    def always_fail():
        raise ValueError("fail")
    with pytest.raises(ValueError):
        always_fail()

def test_context():
    ctx = Context()
    ctx.update_schema('df1', {'col': 'int'})
    assert 'df1' in ctx and ctx['df1']['col'] == 'int'
    ctx['x'] = 5
    assert ctx['x'] == 5

def test_export_docs():
    def foo():
        """Foo does bar."""
    def bar():
        pass
    docs = export_docs([foo, bar])
    assert "# Workflow Documentation" in docs
    assert "## foo" in docs
    assert "Foo does bar." in docs
    assert "## bar" in docs

def test_hook_manager():
    hm = HookManager()
    calls = []
    def pre(a): calls.append(('pre', a))
    def success(a): calls.append(('success', a))
    def failure(a): calls.append(('failure', a))
    hm.register_hook('pre_run', pre)
    hm.register_hook('on_success', success)
    hm.register_hook('on_failure', failure)
    hm.run_hooks('pre_run', 1)
    hm.run_hooks('on_success', 2)
    hm.run_hooks('on_failure', 3)
    assert calls == [('pre', 1), ('success', 2), ('failure', 3)]
    with pytest.raises(ValueError):
        hm.register_hook('unknown', lambda: None)
    with pytest.raises(ValueError):
        hm.run_hooks('unknown')

def test_validate_params():
    schema = {
        'lr': {'type': float, 'required': True, 'min': 0.0, 'max': 1.0},
        'epochs': {'type': int, 'required': True, 'min': 1}
    }
    params = {'lr': 0.1, 'epochs': 10}
    assert validate_params(params, schema) is True
    with pytest.raises(ValueError):
        validate_params({'lr': 'bad', 'epochs': 10}, schema)
    with pytest.raises(ValueError):
        validate_params({'epochs': 10}, schema)
    with pytest.raises(ValueError):
        validate_params({'lr': -0.1, 'epochs': 10}, schema)
    with pytest.raises(ValueError):
        validate_params({'lr': 0.1, 'epochs': 0}, schema)
