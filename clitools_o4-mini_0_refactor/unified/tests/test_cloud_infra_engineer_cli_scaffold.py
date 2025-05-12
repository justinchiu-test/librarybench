import os
import subprocess
import signal
import sys
import tempfile
import uuid
import datetime
import argparse
import ipaddress
import cloud_infra_engineer.keyring as keyring
import pytest
import cloud_infra_engineer.toml as toml
import json
import cloud_infra_engineer.yaml as yaml
from cloud_infra_engineer.cli_scaffold import (
    bump_version, init_package, publish_package, register_hook,
    handle_signals, load_config, env_override, compute_default,
    generate_docs, validate_input, fetch_secret, retry_call
)

class DummyError(Exception):
    pass

def test_bump_version_no_tags(monkeypatch):
    def fake_check_output(cmd, stderr):
        raise subprocess.CalledProcessError(1, cmd)
    monkeypatch.setattr(subprocess, 'check_output', fake_check_output)
    v = bump_version()
    assert v == '0.0.1'

def test_bump_version_with_tag(monkeypatch):
    monkeypatch.setattr(subprocess, 'check_output', lambda *args, **kwargs: b'v1.2.3')
    v = bump_version()
    assert v == '1.2.4'

def test_init_package(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    ok = init_package('testpkg', ['a==1.0', 'b>=2.0'], version="1.0.0")
    assert ok
    data = toml.load(tmp_path / 'pyproject.toml')
    assert data['project']['name'] == 'testpkg'
    assert data['project']['version'] == '1.0.0'
    assert 'a==1.0' in data['project']['dependencies']
    os.chdir(cwd)

def test_publish_package(monkeypatch):
    calls = []
    def fake_check_call(cmd):
        calls.append(cmd)
    monkeypatch.setattr(subprocess, 'check_call', fake_check_call)
    res = publish_package('dist/pkg.whl', 'https://repo', 'user', 'pass')
    assert res is True
    assert 'twine' in calls[0][3]
    assert 'dist/pkg.whl' in calls[0]

def test_register_hook(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    os.makedirs('.git', exist_ok=True)
    hook = register_hook('pre-commit', '/path/to/script.sh')
    assert os.path.isfile(hook)
    with open(hook) as f:
        content = f.read()
    assert 'exec /path/to/script.sh' in content
    os.chdir(cwd)

def test_handle_signals(monkeypatch, capsys):
    @handle_signals
    def f():
        os.kill(os.getpid(), signal.SIGINT)
    with pytest.raises(SystemExit) as e:
        f()
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "Operation aborted." in captured.out

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def test_load_config_ini(tmp_path):
    p = tmp_path / 'cfg.ini'
    write_file(p, "[a]\nx=1\ny=hello")
    cfg = load_config(str(p))
    assert 'a' in cfg and cfg['a']['x'] == '1'

def test_load_config_json(tmp_path):
    p = tmp_path / 'cfg.json'
    write_file(p, json.dumps({'x': 2}))
    cfg = load_config(str(p))
    assert cfg['x'] == 2

def test_load_config_yaml(tmp_path):
    p = tmp_path / 'cfg.yaml'
    write_file(p, yaml.dump({'x': 3}))
    cfg = load_config(str(p))
    assert cfg['x'] == 3

def test_load_config_toml(tmp_path):
    p = tmp_path / 'cfg.toml'
    write_file(p, toml.dumps({'x': 4}))
    cfg = load_config(str(p))
    assert cfg['x'] == 4

def test_env_override(monkeypatch):
    cfg = {'a': '1', 'b': '2'}
    monkeypatch.setenv('CLOUD_A', '10')
    out = env_override(cfg)
    assert out['a'] == '10'
    assert out['b'] == '2'

def test_compute_default_timestamp():
    name = compute_default(use_uuid=False, prefix='pr')
    assert name.startswith('pr-')
    ts = name.split('-',1)[1]
    datetime.datetime.strptime(ts, '%Y%m%d%H%M%S')

def test_compute_default_uuid():
    name = compute_default(use_uuid=True, prefix='pr')
    assert name.startswith('pr-')
    uuid.UUID(name.split('-',1)[1])

def test_generate_docs(tmp_path):
    parser = argparse.ArgumentParser(prog='prog')
    parser.add_argument('--opt', help='option')
    md = tmp_path / 'doc.md'
    man = tmp_path / 'doc.1'
    ok = generate_docs(parser, str(md), str(man))
    assert ok
    assert md.exists() and man.exists()
    assert 'Usage' in md.read_text()

def test_validate_input_cidr():
    net = validate_input('192.168.0.0/24', 'cidr')
    assert isinstance(ipaddress.ip_network(net), ipaddress.IPv4Network)
    with pytest.raises(ValueError):
        validate_input('notcidr', 'cidr')

def test_validate_input_port():
    assert validate_input('80', 'port') == 80
    with pytest.raises(ValueError):
        validate_input('70000', 'port')

def test_validate_input_path(tmp_path):
    f = tmp_path / 'f.txt'
    f.write_text('x')
    p = validate_input(str(f), 'path')
    assert os.path.isabs(p)
    with pytest.raises(ValueError):
        validate_input(str(f.parent / 'nope'), 'path')

def test_validate_input_coercion():
    assert validate_input('5', 'int') == 5
    assert isinstance(validate_input('3.14', 'float'), float)
    assert validate_input(123, 'str') == '123'

def test_fetch_secret_keyring(monkeypatch):
    monkeypatch.setattr(keyring, 'get_password', lambda svc, name: 'sec')
    assert fetch_secret('mysecret') == 'sec'
    with pytest.raises(ValueError):
        monkeypatch.setattr(keyring, 'get_password', lambda svc, name: None)
        fetch_secret('other')

def test_retry_call_success_after_failures():
    calls = {'count':0}
    @retry_call(max_attempts=3, backoff_factor=0)
    def flaky():
        calls['count'] +=1
        if calls['count'] < 3:
            raise DummyError()
        return 'ok'
    assert flaky() == 'ok'
    assert calls['count'] == 3

def test_retry_call_exceed(monkeypatch):
    @retry_call(max_attempts=2, backoff_factor=0)
    def always_fail():
        raise DummyError("fail")
    with pytest.raises(DummyError):
        always_fail()
