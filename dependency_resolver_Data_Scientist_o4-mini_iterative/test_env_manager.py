import os
import json
import tempfile
import shutil
import pytest

import env_manager as em

# Helper to write index.json
def write_index(path, packages):
    with open(path, 'w') as f:
        json.dump(packages, f)

# Helper to create offline dir
def write_offline(offline_dir, packages):
    os.makedirs(offline_dir, exist_ok=True)
    for pkg in packages:
        fname = f"{pkg['name']}-{pkg['version']}.json"
        with open(os.path.join(offline_dir, fname), 'w') as f:
            json.dump(pkg, f)

@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

def test_create_env(tmp_path):
    env = tmp_path / 'env1'
    em.create_env(str(env))
    assert os.path.isdir(str(env))
    meta = json.load(open(env / 'env.json'))
    assert meta == {'packages': {}}
    # creating again should error
    with pytest.raises(ValueError):
        em.create_env(str(env))

def test_install_without_offline(tmp_path):
    # prepare index
    idx = tmp_path / 'index.json'
    packages = [
        {"name": "A", "version": "1.0", "dependencies": {"B": ">=1.0"}},
        {"name": "B", "version": "1.0", "dependencies": {}},
    ]
    write_index(str(idx), packages)
    # create env
    env = tmp_path / 'env2'
    em.create_env(str(env))
    em.install_packages(str(env), ["A"], index_file=str(idx))
    meta = json.load(open(env / 'env.json'))
    assert "A" in meta['packages']
    assert "B" in meta['packages']
    assert meta['packages']["A"]['installed_from'] is None
    assert meta['packages']["B"]['installed_from'] == "A"

def test_install_with_offline(tmp_path):
    # offline dir with a single package
    offline = tmp_path / 'off'
    pkg = {"name": "C", "version": "0.9", "dependencies": {}}
    write_offline(str(offline), [pkg])
    env = tmp_path / 'env3'
    em.create_env(str(env))
    em.install_packages(str(env), ["C"], offline_dir=str(offline))
    meta = json.load(open(env / 'env.json'))
    assert "C" in meta['packages']
    assert meta['packages']["C"]['version'] == "0.9"

def test_lockfile_and_export(tmp_path):
    idx = tmp_path / 'index.json'
    packages = [{"name": "X", "version": "1.2", "dependencies": {}}]
    write_index(str(idx), packages)
    env = tmp_path / 'env4'
    em.create_env(str(env))
    em.install_packages(str(env), ["X"], index_file=str(idx))
    # generate lockfile
    lock = tmp_path / 'lock.txt'
    em.generate_lockfile(str(env), str(lock))
    content = open(lock).read().strip()
    assert content == "X==1.2"
    # export env same
    lock2 = tmp_path / 'export.txt'
    em.export_env(str(env), str(lock2))
    assert open(lock2).read().strip() == content

def test_check_package_installed(tmp_path):
    env = tmp_path / 'env5'
    em.create_env(str(env))
    assert not em.check_package_installed(str(env), "Z")
    # add manually
    meta = {'packages': {"Z": {"version":"0.1","dependencies":{}, "installed_from":None}}}
    json.dump(meta, open(env/'env.json','w'))
    assert em.check_package_installed(str(env), "Z")

def test_check_updates(tmp_path):
    # index with multiple versions
    idx = tmp_path / 'index.json'
    pkgs = [
        {"name": "U", "version": "1.0", "dependencies": {}},
        {"name": "U", "version": "2.0", "dependencies": {}}
    ]
    write_index(str(idx), pkgs)
    env = tmp_path / 'env6'
    em.create_env(str(env))
    em.install_packages(str(env), ["U==1.0"], index_file=str(idx))
    updates = em.check_updates(str(env), index_file=str(idx))
    assert "U" in updates
    assert updates["U"]['current'] == "1.0"
    assert updates["U"]['latest'] == "2.0"

def test_import_env(tmp_path):
    # prepare index and lockfile
    idx = tmp_path / 'index.json'
    packages = [
        {"name": "P", "version": "0.5", "dependencies": {}}
    ]
    write_index(str(idx), packages)
    lock = tmp_path / 'lock2.txt'
    lock.write_text("P==0.5\n")
    env_imp = tmp_path / 'env7'
    em.import_env(str(env_imp), str(lock), index_file=str(idx))
    assert em.check_package_installed(str(env_imp), "P")
    meta = json.load(open(env_imp / 'env.json'))
    assert meta['packages']['P']['version'] == "0.5"

def test_dependency_solver(tmp_path):
    idx = tmp_path / 'index.json'
    packages = [
        {"name": "D", "version": "1.0", "dependencies": {}},
        {"name": "D", "version": "2.0", "dependencies": {}},
        {"name": "E", "version": "1.0", "dependencies": {"D": ">=1.0,<2.0"}}
    ]
    write_index(str(idx), packages)
    env = tmp_path / 'env8'
    em.create_env(str(env))
    em.install_packages(str(env), ["E"], index_file=str(idx))
    meta = json.load(open(env / 'env.json'))
    # D should be 1.0 due to constraint
    assert meta['packages']['D']['version'] == "1.0"
    # installing D>=2.0 should pick 2.0
    env2 = tmp_path / 'env9'
    em.create_env(str(env2))
    em.install_packages(str(env2), ["D>=2.0"], index_file=str(idx))
    meta2 = json.load(open(env2 / 'env.json'))
    assert meta2['packages']['D']['version'] == "2.0"

def test_security_vulnerabilities(tmp_path):
    # use bundled vulnerability_db.json
    env = tmp_path / 'env10'
    em.create_env(str(env))
    # manually add vulnerable pkgA 1.0
    meta = {'packages': {"pkgA": {"version":"1.0","dependencies":{}, "installed_from":None}}}
    json.dump(meta, open(env/'env.json','w'), indent=2)
    alerts = em.check_vulnerabilities(str(env))
    assert "pkgA" in alerts
    assert alerts["pkgA"] == "1.0"
    # no alert for non-vuln
    meta2 = {'packages': {"pkgA": {"version":"3.0","dependencies":{}, "installed_from":None}}}
    json.dump(meta2, open(env/'env.json','w'), indent=2)
    alerts2 = em.check_vulnerabilities(str(env))
    assert alerts2 == {}

def test_dependency_explanation(tmp_path):
    # index with nested deps
    idx = tmp_path / 'index.json'
    packages = [
        {"name": "Root", "version": "1.0", "dependencies": {"A": ">=1.0"}},
        {"name": "A", "version": "1.1", "dependencies": {"B": "==2.0"}},
        {"name": "B", "version": "2.0", "dependencies": {}}
    ]
    write_index(str(idx), packages)
    env = tmp_path / 'env11'
    em.create_env(str(env))
    em.install_packages(str(env), ["Root"], index_file=str(idx))
    explanation = em.dependency_explanation(str(env), "Root")
    # Expect lines in order
    lines = explanation.splitlines()
    assert lines[0].startswith("Root==1.0")
    assert lines[1].strip().startswith("A==1.1")
    assert lines[2].strip().startswith("B==2.0")

def test_errors(tmp_path):
    idx = tmp_path / 'index.json'
    write_index(str(idx), [])
    env = tmp_path / 'env12'
    em.create_env(str(env))
    # install missing package
    with pytest.raises(ValueError):
        em.install_packages(str(env), ["Missing"], index_file=str(idx))
    # import missing lockfile
    with pytest.raises(ValueError):
        em.import_env(str(env), str(tmp_path / 'nope.txt'))
    # check vulnerability db missing
    # point to non-existent file
    with pytest.raises(ValueError):
        em.check_vulnerabilities(str(env), vulnerability_db_file=str(tmp_path / 'no.db'))
