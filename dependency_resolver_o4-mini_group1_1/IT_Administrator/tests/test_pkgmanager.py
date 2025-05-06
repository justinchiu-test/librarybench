import os
import json
import pytest
import sys

# ensure the root dir is on path to import IT_Administrator.pkgmanager
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import IT_Administrator.pkgmanager

@pytest.fixture
def temp_root(tmp_path):
    return str(tmp_path)

@pytest.fixture
def manager(temp_root):
    return pkgmanager.PackageManager(temp_root)

def test_create_and_delete_environment(manager):
    # create
    env = manager.create_environment("env1")
    assert "env1" in manager.list_environments()
    # cannot create again
    with pytest.raises(pkgmanager.EnvironmentError):
        manager.create_environment("env1")
    # delete
    manager.delete_environment("env1")
    assert "env1" not in manager.list_environments()
    # deleting non-existent
    with pytest.raises(pkgmanager.EnvironmentError):
        manager.delete_environment("env1")

def test_switch_environment(manager):
    manager.create_environment("a")
    env_a = manager.switch_environment("a")
    assert manager.get_current_environment().name == "a"
    # switching to new existing on disk
    manager.create_environment("b")
    env_b = manager.switch_environment("b")
    assert env_b.name == "b"
    # switch non-existent
    with pytest.raises(pkgmanager.EnvironmentError):
        manager.switch_environment("nope")

def test_install_and_list_packages(manager):
    env = manager.create_environment("env")
    manager.switch_environment("env")
    cur = manager.get_current_environment()
    # install with version
    cur.install_package("foo", "1.2.3")
    cur.install_package("bar", "0.1.0")
    pkgs = cur.list_packages()
    assert pkgs == {"foo": "1.2.3", "bar": "0.1.0"}

def test_generate_and_install_from_lockfile(manager, tmp_path):
    env1 = manager.create_environment("e1")
    manager.switch_environment("e1")
    env1.install_package("pkga", "1.0.0")
    env1.install_package("pkgb", "2.0.0")
    lockfile = env1.generate_lockfile()
    assert os.path.exists(lockfile)
    # content
    data = json.loads(lockfile and open(lockfile).read())
    assert data["environment"] == "e1"
    assert data["packages"] == {"pkga": "1.0.0", "pkgb": "2.0.0"}
    # install from lockfile into new env
    env2 = manager.create_environment("e2")
    env2.install_from_lockfile(lockfile)
    assert env2.list_packages() == {"pkga": "1.0.0", "pkgb": "2.0.0"}

def test_remove_package(manager):
    env = manager.create_environment("env")
    env.install_package("x", "0.0.1")
    assert "x" in env.list_packages()
    env.remove_package("x")
    assert env.list_packages() == {}
    with pytest.raises(pkgmanager.EnvironmentError):
        env.remove_package("x")

def test_vulnerability_alerts(manager):
    env = manager.create_environment("sec")
    # use default vuln db: openssl 1.0.0 vulnerable
    env.install_package("openssl", "1.0.0")
    env.install_package("safe", "9.9.9")
    alerts = env.check_vulnerabilities()
    assert alerts == [{"package": "openssl", "version": "1.0.0"}]
    # custom db
    custom = {"safe": ["9.9.9"]}
    alerts2 = env.check_vulnerabilities(vuln_db=custom)
    assert alerts2 == [{"package": "safe", "version": "9.9.9"}]

def test_rollback(manager):
    env = manager.create_environment("rb")
    # initial state empty
    with pytest.raises(pkgmanager.EnvironmentError):
        env.rollback()
    env.install_package("pkg", "1.0")
    env.install_package("pkg", "2.0")
    assert env.list_packages()["pkg"] == "2.0"
    env.rollback()
    assert env.list_packages()["pkg"] == "1.0"
    # multiple rollbacks
    env.rollback()
    assert env.list_packages() == {}
    with pytest.raises(pkgmanager.EnvironmentError):
        env.rollback()

def test_version_pinning_and_install(manager):
    env = manager.create_environment("pin")
    # pin without install
    env.pin_version("mypkg", "3.3.3")
    # install without version uses pin
    env.install_package("mypkg")
    assert env.list_packages()["mypkg"] == "3.3.3"
    # override pin by specifying version
    env.install_package("mypkg", "4.4.4")
    assert env.list_packages()["mypkg"] == "4.4.4"
    # pin updated
    env.pin_version("mypkg", "5.5.5")
    env.remove_package("mypkg")
    env.install_package("mypkg")
    assert env.list_packages()["mypkg"] == "5.5.5"
