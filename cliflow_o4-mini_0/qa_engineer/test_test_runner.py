import os
import json
import configparser
import tempfile
import pytest
from getpass import getpass
import test_runner as tr

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def test_load_config_json(tmp_path):
    data = {"key": "value"}
    path = tmp_path / "conf.json"
    write_file(path, json.dumps(data))
    cfg = tr.load_config(str(path))
    assert cfg == data

@pytest.mark.skipif(tr.yaml is None, reason="yaml not available")
def test_load_config_yaml(tmp_path):
    data = {"a": 1}
    path = tmp_path / "conf.yaml"
    yaml_content = "a: 1\n"
    write_file(path, yaml_content)
    cfg = tr.load_config(str(path))
    assert cfg == data

@pytest.mark.skipif(tr.toml is None, reason="toml not available")
def test_load_config_toml(tmp_path):
    data = {"a": 1}
    path = tmp_path / "conf.toml"
    toml_content = "a = 1\n"
    write_file(path, toml_content)
    cfg = tr.load_config(str(path))
    assert cfg == data

def test_load_config_ini(tmp_path):
    path = tmp_path / "conf.ini"
    config = configparser.ConfigParser()
    config['section'] = {'key': 'value'}
    with open(path, 'w') as f:
        config.write(f)
    cfg = tr.load_config(str(path))
    assert cfg == {'section': {'key': 'value'}}

def test_run_dry_run():
    plan = [{'name': 't1'}, {'name': 't2'}]
    assert tr.run_dry_run(plan) == ['t1', 't2']

def test_branch_flow_pass():
    mapping = {'pass': ['a'], 'fail': ['b']}
    assert tr.branch_flow(0, mapping) == ['a']

def test_branch_flow_fail():
    mapping = {'pass': ['a'], 'fail': ['b']}
    assert tr.branch_flow(1, mapping) == ['b']

def test_prompt_interactive(monkeypatch, capsys):
    monkeypatch.setattr('builtins.input', lambda prompt='': '2')
    choice = tr.prompt_interactive("Choose:", ['x', 'y', 'z'])
    captured = capsys.readouterr()
    assert "Choose:" in captured.out
    assert choice == 'y'

def test_secure_prompt(monkeypatch):
    monkeypatch.setattr('test_runner.getpass', lambda prompt='': 'secret')
    val = tr.secure_prompt("Enter:")
    assert val == 'secret'

def test_retry_success():
    calls = {'count': 0}
    @tr.retry(retries=2, backoff=0)
    def flaky():
        calls['count'] += 1
        if calls['count'] < 2:
            raise ValueError("fail")
        return "ok"
    assert flaky() == "ok"
    assert calls['count'] == 2

def test_retry_fail():
    @tr.retry(retries=1, backoff=0)
    def always_fail():
        raise RuntimeError("nope")
    with pytest.raises(RuntimeError):
        always_fail()

def test_export_docs_markdown():
    plan = [{'name': 't1', 'desc': 'd1'}]
    md = tr.export_docs(plan, format='markdown')
    assert "# Test Plan" in md
    assert "- **t1**: d1" in md

def test_export_docs_html():
    plan = [{'name': 't1', 'desc': 'd1'}]
    html = tr.export_docs(plan, format='html')
    assert "<h1>Test Plan</h1>" in html
    assert "<li><strong>t1</strong>: d1</li>" in html

def test_export_docs_invalid():
    with pytest.raises(ValueError):
        tr.export_docs([], format='xml')

def test_validate_params_valid():
    tr.validate_params('dev_env', 'chrome', ['tag1', 'tag-2'])

def test_validate_params_invalid_env():
    with pytest.raises(ValueError):
        tr.validate_params('InvalidEnv!', 'chrome', ['tag'])

def test_validate_params_invalid_browser():
    with pytest.raises(ValueError):
        tr.validate_params('dev', 'ie', ['tag'])

def test_validate_params_invalid_tags():
    with pytest.raises(ValueError):
        tr.validate_params('dev', 'chrome', ['good', 'bad tag'])

def test_context():
    ctx = tr.Context()
    ctx.add_artifact('a', 123)
    ctx.add_log('log1')
    ctx.set_result('t1', True)
    assert ctx.artifacts['a'] == 123
    assert 'log1' in ctx.logs
    assert ctx.results['t1'] is True

def test_register_and_run_hooks():
    calls = []
    def on_complete(arg):
        calls.append(arg)
    tr.register_hook('on_complete', on_complete)
    # Accessing internal _run_hooks for test
    tr._run_hooks('on_complete', 'done')
    assert 'done' in calls

def test_register_hook_invalid():
    with pytest.raises(ValueError):
        tr.register_hook('unknown_event', lambda: None)
