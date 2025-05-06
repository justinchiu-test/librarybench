import os
import json
import tempfile
import shutil
import pytest

from DevOps_Engineer.env_manager import PackageSource, EnvironmentManager, Version

# Sample package store for testing
SAMPLE_STORE = {
    'A': {
        '1.0': {'requires': {}, 'vulns': []},
        '2.0': {'requires': {'B': '>=1.0'}, 'vulns': []},
    },
    'B': {
        '1.0': {'requires': {}, 'vulns': ['CVE-1234']},
        '2.0': {'requires': {}, 'vulns': []},
    },
    'C': {
        '1.0': {'requires': {'A': '>=1.0'}, 'vulns': []},
        '2.0': {'requires': {'A': '>=2.0'}, 'vulns': []},
    },
    'D': {
        '0.1': {'requires': {}, 'vulns': []},
    }
}

@pytest.fixture
def source():
    return PackageSource(SAMPLE_STORE)

@pytest.fixture
def tmp_env_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)

def test_install_and_exists(source):
    env = EnvironmentManager(source)
    env.install('A')
    # A latest is 2.0, should bring in B>=1.0 -> B 2.0
    assert env.package_exists('A')
    assert env.package_exists('B')
    assert str(env.installed['A']) == '2.0'
    assert str(env.installed['B']) == '2.0'

def test_offline_installation(source):
    env = EnvironmentManager(source)
    # offline install should work the same since source simulates local
    env.install('D', offline=True)
    assert env.package_exists('D')
    assert str(env.installed['D']) == '0.1'

def test_lockfile_generation(source, tmp_env_dir):
    env = EnvironmentManager(source, env_path=tmp_env_dir)
    env.install('A')
    lockfile = os.path.join(tmp_env_dir, 'lock.json')
    env.generate_lockfile(lockfile)
    with open(lockfile) as f:
        data = json.load(f)
    assert 'packages' in data
    assert data['packages']['A'] == '2.0'
    assert data['packages']['B'] == '2.0'

def test_virtual_env_management(source, tmp_env_dir):
    env = EnvironmentManager(source, env_path=tmp_env_dir)
    # create new env
    env.install('D')
    # config file should exist
    config_path = os.path.join(tmp_env_dir, EnvironmentManager.CONFIG_FILE)
    assert os.path.isfile(config_path)
    # load into new manager
    env2 = EnvironmentManager(source, env_path=tmp_env_dir)
    assert env2.package_exists('D')
    assert str(env2.installed['D']) == '0.1'

def test_notify_updates(source):
    env = EnvironmentManager(source)
    # install older version explicitly
    env.install('B', version='1.0')
    updates = env.notify_updates()
    assert 'B' in updates
    assert updates['B']['current'] == '1.0'
    assert updates['B']['latest'] == '2.0'
    # no updates for A (not installed)
    assert 'A' not in updates

def test_export_import_env(source, tmp_env_dir):
    env = EnvironmentManager(source)
    env.install('C')  # installs C 2.0 -> A2.0->B2.0
    export_path = os.path.join(tmp_env_dir, 'export.json')
    env.export_env(export_path)
    # import into new env
    env2 = EnvironmentManager(source)
    env2.import_env(export_path)
    assert env2.package_exists('C')
    assert env2.package_exists('A')
    assert env2.package_exists('B')
    assert str(env2.installed['C']) == '2.0'

def test_dependency_solver(source):
    env = EnvironmentManager(source)
    # solve constraints for A>=1.0 and C>=1.0
    env.solve_and_install(['A>=1.0', 'C>=1.0'])
    # C latest is 2.0, requires A>=2.0 -> A2.0,B2.0
    assert env.package_exists('A') and str(env.installed['A']) == '2.0'
    assert env.package_exists('B') and str(env.installed['B']) == '2.0'
    assert env.package_exists('C') and str(env.installed['C']) == '2.0'

def test_security_alerts(source):
    env = EnvironmentManager(source)
    env.install('B', version='1.0')
    alerts = env.security_alerts()
    assert 'B' in alerts
    assert 'CVE-1234' in alerts['B']
    # installing non-vuln
    env2 = EnvironmentManager(source)
    env2.install('B', version='2.0')
    assert env2.security_alerts() == {}

def test_explain_dependency(source):
    env = EnvironmentManager(source)
    env.solve_and_install(['C>=1.0'])
    # possible chains: C->A->B or C->A (A->B dependent)
    chains = env.explain('C')
    # Each chain should start with C and end with leaf
    assert any(chain[0] == 'C' for chain in chains)
    # Explain A
    achains = env.explain('A')
    assert any(chain[0] == 'A' for chain in achains)

def test_missing_package(source):
    env = EnvironmentManager(source)
    with pytest.raises(KeyError):
        env.install('X')

def test_constraint_no_match(source):
    env = EnvironmentManager(source)
    with pytest.raises(KeyError):
        env.solve_and_install(['A<1.0'])
