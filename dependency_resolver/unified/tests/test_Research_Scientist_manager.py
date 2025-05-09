import os
import json
import tarfile
import shutil
import pytest
from click.testing import CliRunner
import env_manager

# Helpers to create fake package tar.gz
def make_package(repo_dir, name, version, dependencies=None):
    pkg_name = f"{name}-{version}"
    pkg_dir = os.path.join(repo_dir, pkg_name)
    os.makedirs(pkg_dir, exist_ok=True)
    meta = {'name': name, 'version': version, 'dependencies': dependencies or []}
    with open(os.path.join(pkg_dir, 'metadata.json'), 'w') as f:
        json.dump(meta, f)
    tar_path = os.path.join(repo_dir, f"{pkg_name}.tar.gz")
    with tarfile.open(tar_path, 'w:gz') as tf:
        tf.add(os.path.join(pkg_dir, 'metadata.json'), arcname='metadata.json')
    shutil.rmtree(pkg_dir)
    return tar_path

@pytest.fixture
def runner(tmp_path, monkeypatch):
    # Set ENV_MANAGER_ROOT
    root = tmp_path / 'envroot'
    monkeypatch.setenv('ENV_MANAGER_ROOT', str(root))
    # Ensure modules pick up new root
    import importlib
    importlib.reload(env_manager)
    return CliRunner()

@pytest.fixture
def setup_repo(tmp_path, runner):
    repo = tmp_path / 'repo'
    repo.mkdir()
    # A v1.0 no deps
    make_package(str(repo), 'A', '1.0', [])
    make_package(str(repo), 'A', '2.0', [])
    # B depends on A>=1.0
    make_package(str(repo), 'B', '1.0', ['A>=1.0'])
    return str(repo)

def test_repo_add_and_list(runner, setup_repo):
    result = runner.invoke(env_manager.main, ['repo', 'add', 'test', setup_repo])
    assert result.exit_code == 0
    res = runner.invoke(env_manager.main, ['repo', 'list'])
    assert 'test: ' in res.output

def test_env_create_list_switch(runner):
    # create two envs
    runner.invoke(env_manager.main, ['env', 'create', 'e1'])
    runner.invoke(env_manager.main, ['env', 'create', 'e2'])
    res = runner.invoke(env_manager.main, ['env', 'list'])
    assert 'e1' in res.output and 'e2' in res.output
    # switch to e1
    runner.invoke(env_manager.main, ['env', 'switch', 'e1'])
    res2 = runner.invoke(env_manager.main, ['env', 'list'])
    assert '* e1' in res2.output

def test_install_and_list_packages(runner, setup_repo):
    # setup repo and env
    runner.invoke(env_manager.main, ['repo', 'add', 'r', setup_repo])
    runner.invoke(env_manager.main, ['env', 'create', 'env1'])
    runner.invoke(env_manager.main, ['env', 'switch', 'env1'])
    # install B, should install A and B
    res = runner.invoke(env_manager.main, ['install', 'B'])
    assert res.exit_code == 0
    # list packages
    res2 = runner.invoke(env_manager.main, ['list'])
    assert 'A==2.0' in res2.output
    assert 'B==1.0' in res2.output

def test_show_metadata(runner, setup_repo):
    runner.invoke(env_manager.main, ['repo', 'add', 'r', setup_repo])
    runner.invoke(env_manager.main, ['env', 'create', 'env1'])
    runner.invoke(env_manager.main, ['env', 'switch', 'env1'])
    runner.invoke(env_manager.main, ['install', 'B'])
    res = runner.invoke(env_manager.main, ['show', 'B'])
    meta = json.loads(res.output)
    assert meta['name']=='B' and 'A>=1.0' in meta['dependencies']

def test_rollback_on_error(runner, setup_repo):
    runner.invoke(env_manager.main, ['repo', 'add', 'r', setup_repo])
    runner.invoke(env_manager.main, ['env', 'create', 'e'])
    runner.invoke(env_manager.main, ['env', 'switch', 'e'])
    # install A successfully
    runner.invoke(env_manager.main, ['install', 'A'])
    # now attempt to install non-existent C, should error and revert to only A
    res = runner.invoke(env_manager.main, ['install', 'C'])
    assert res.exit_code != 0
    # list should still show A only
    res2 = runner.invoke(env_manager.main, ['list'])
    assert 'A==2.0' in res2.output and 'C' not in res2.output

def test_lock_and_install_lockfile(runner, setup_repo, tmp_path):
    runner.invoke(env_manager.main, ['repo', 'add', 'r', setup_repo])
    runner.invoke(env_manager.main, ['env', 'create', 'orig'])
    runner.invoke(env_manager.main, ['env', 'switch', 'orig'])
    runner.invoke(env_manager.main, ['install', 'B'])
    lockfile = str(tmp_path / 'lock.json')
    runner.invoke(env_manager.main, ['lock', lockfile])
    # create new env from lockfile
    res = runner.invoke(env_manager.main, ['install-lockfile', lockfile, 'newenv'])
    assert res.exit_code == 0
    # list envs includes newenv
    res2 = runner.invoke(env_manager.main, ['env', 'list'])
    assert 'newenv' in res2.output
    # switch and list pkgs
    runner.invoke(env_manager.main, ['env', 'switch', 'newenv'])
    res3 = runner.invoke(env_manager.main, ['list'])
    assert 'A==2.0' in res3.output and 'B==1.0' in res3.output

def test_offline_install(runner, setup_repo):
    # initial install to cache
    runner.invoke(env_manager.main, ['repo', 'add', 'r', setup_repo])
    runner.invoke(env_manager.main, ['env', 'create', 'e'])
    runner.invoke(env_manager.main, ['env', 'switch', 'e'])
    runner.invoke(env_manager.main, ['install', 'A'])
    # remove repos to simulate offline
    res_repo = runner.invoke(env_manager.main, ['repo', 'list'])
    # monkeypatch repos.json to empty
    with open(env_manager.REPOS_FILE, 'w') as f:
        json.dump([], f)
    # uninstall A
    runner.invoke(env_manager.main, ['uninstall', 'A'])
    # offline install A
    res = runner.invoke(env_manager.main, ['install', 'A', '--offline'])
    assert res.exit_code == 0
    res2 = runner.invoke(env_manager.main, ['list'])
    assert 'A==2.0' in res2.output

def test_batch_install_and_uninstall(runner, setup_repo):
    runner.invoke(env_manager.main, ['repo', 'add', 'r', setup_repo])
    runner.invoke(env_manager.main, ['env', 'create', 'e'])
    runner.invoke(env_manager.main, ['env', 'switch', 'e'])
    runner.invoke(env_manager.main, ['install', 'A', 'B'])
    res = runner.invoke(env_manager.main, ['list'])
    assert 'A==2.0' in res.output and 'B==1.0' in res.output
    # uninstall both
    runner.invoke(env_manager.main, ['uninstall', 'A', 'B'])
    res2 = runner.invoke(env_manager.main, ['list'])
    assert res2.output.strip()==''

