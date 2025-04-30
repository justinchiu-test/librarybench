import os
import json
import tempfile
import pytest
from click.testing import CliRunner
from env_manager.cli import cli

@pytest.fixture
def runner(tmp_path, monkeypatch):
    root = tmp_path / "envs"
    monkeypatch.setenv('ENVMGR_ROOT', str(root))
    return CliRunner()

def test_cli_env_commands(runner):
    r = runner.invoke(cli, ['env','create','foo'])
    assert "Created environment 'foo'." in r.stdout
    r = runner.invoke(cli, ['env','list'])
    assert 'foo' in r.stdout
    r = runner.invoke(cli, ['env','delete','foo'])
    assert "Deleted environment 'foo'." in r.stdout

def test_cli_install_and_check(runner):
    runner.invoke(cli, ['env','create','bar'])
    r = runner.invoke(cli, ['install','--env','bar','C'])
    assert "Installed C into 'bar'." in r.stdout
    r2 = runner.invoke(cli, ['check','--env','bar','C'])
    assert 'True' in r2.stdout

def test_cli_explain(runner):
    runner.invoke(cli, ['env','create','baz'])
    runner.invoke(cli, ['install','--env','baz','A'])
    r = runner.invoke(cli, ['explain','--env','baz','A'])
    assert 'A==' in r.stdout

def test_cli_lockfile(runner, tmp_path):
    runner.invoke(cli, ['env','create','lf1'])
    runner.invoke(cli, ['install','--env','lf1','B'])
    lock = tmp_path / "lf.json"
    r = runner.invoke(cli, ['lockfile','export','--env','lf1','--output',str(lock)])
    assert lock.exists()
    runner.invoke(cli, ['env','create','lf2'])
    r2 = runner.invoke(cli, ['lockfile','install','--env','lf2','--file',str(lock)])
    assert "Installed from lockfile into lf2" in r2.stdout

def test_cli_import(runner, tmp_path):
    runner.invoke(cli, ['env','create','imp1'])
    spec = {"packages":["C"]}
    f = tmp_path / "s.json"
    f.write_text(json.dumps(spec))
    r = runner.invoke(cli, ['import-env','--env','imp1','--file',str(f)])
    assert "Imported environment spec" in r.stdout

def test_cli_repos(runner, tmp_path):
    # create a fake repo
    data = {"Z":{"0.1": []}}
    repof = tmp_path/"r.json"
    repof.write_text(json.dumps(data))
    r1 = runner.invoke(cli, ['repos','add',str(repof)])
    assert "Added repo" in r1.stdout
    r2 = runner.invoke(cli, ['repos','list'])
    assert str(repof) in r2.stdout
    r3 = runner.invoke(cli, ['repos','remove',str(repof)])
    assert "Removed repo" in r3.stdout

def test_cli_updates(runner):
    runner.invoke(cli, ['env','create','u1'])
    # install B@1.0 manually
    runner.invoke(cli, ['install','--env','u1','B'])
    # simulate that default chosen is latest 1.1, so no updates
    r = runner.invoke(cli, ['updates','--env','u1'])
    assert "All packages up-to-date." in r.stdout
