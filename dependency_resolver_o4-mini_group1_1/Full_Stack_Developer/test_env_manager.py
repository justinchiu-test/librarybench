import os
import json
import pytest
from Full_Stack_Developer.env_manager import EnvironmentManager

def setup_vuln_db(path, vulns):
    with open(path, "w") as f:
        json.dump(vulns, f)

@pytest.fixture
def temp_manager(tmp_path):
    # Create a vulnerability DB file
    vuln_db = tmp_path / "vulnerabilities.json"
    vuln_db.write_text("[]")
    mgr = EnvironmentManager(base_dir=str(tmp_path), vuln_db_path=str(vuln_db))
    return tmp_path, mgr

def test_create_and_list_envs(temp_manager):
    tmp, mgr = temp_manager
    mgr.create_env("dev")
    mgr.create_env("prod")
    assert sorted(mgr.list_envs()) == ["dev", "prod"]
    with pytest.raises(ValueError):
        mgr.create_env("dev")

def test_delete_env(temp_manager):
    tmp, mgr = temp_manager
    mgr.create_env("dev")
    mgr.delete_env("dev")
    assert mgr.list_envs() == []
    with pytest.raises(ValueError):
        mgr.delete_env("dev")

def test_delete_current_env_resets_current(temp_manager):
    tmp, mgr = temp_manager
    mgr.create_env("dev")
    mgr.switch_env("dev")
    assert mgr.get_current_env() == "dev"
    mgr.delete_env("dev")
    assert mgr.get_current_env() is None

def test_switch_and_get_current_env(temp_manager):
    tmp, mgr = temp_manager
    mgr.create_env("a")
    mgr.create_env("b")
    mgr.switch_env("a")
    assert mgr.get_current_env() == "a"
    mgr.switch_env("b")
    assert mgr.get_current_env() == "b"
    with pytest.raises(ValueError):
        mgr.switch_env("nope")

def test_install_and_remove_package(temp_manager):
    tmp, mgr = temp_manager
    mgr.create_env("dev")
    mgr.switch_env("dev")
    mgr.install_package("pkg1", "1.0.0")
    env_file = tmp / ".envs" / "dev" / "env.json"
    data = json.loads(env_file.read_text())
    assert data["packages"]["pkg1"] == "1.0.0"
    mgr.remove_package("pkg1")
    data2 = json.loads(env_file.read_text())
    assert "pkg1" not in data2["packages"]
    with pytest.raises(ValueError):
        mgr.remove_package("pkg1")

def test_install_without_env(temp_manager):
    _, mgr = temp_manager
    with pytest.raises(ValueError):
        mgr.install_package("x", "1.2.3")

def test_lockfile_generation_and_install(temp_manager):
    tmp, mgr = temp_manager
    mgr.create_env("dev")
    mgr.switch_env("dev")
    mgr.install_package("p1", "1.0")
    mgr.generate_lockfile()
    # Add another package
    mgr.install_package("p2", "2.0")
    data = json.loads((tmp/".envs"/"dev"/"env.json").read_text())
    assert "p2" in data["packages"]
    # Roll back to lockfile
    mgr.install_from_lockfile()
    data2 = json.loads((tmp/".envs"/"dev"/"env.json").read_text())
    assert "p2" not in data2["packages"]
    assert data2["packages"]["p1"] == "1.0"

def test_vulnerability_alerts(temp_manager):
    tmp, mgr = temp_manager
    vulns = [{"name": "badpkg", "version": "0.1"}]
    setup_vuln_db(tmp/"vulnerabilities.json", vulns)
    mgr.create_env("env1")
    mgr.switch_env("env1")
    mgr.install_package("badpkg", "0.1")
    mgr.install_package("goodpkg", "2.0")
    alerts = mgr.alert_vulnerabilities()
    assert alerts == vulns

def test_snapshot_and_rollback(temp_manager):
    tmp, mgr = temp_manager
    mgr.create_env("env2")
    mgr.switch_env("env2")
    # First install
    mgr.install_package("a", "1.0")
    # Second install
    mgr.install_package("b", "2.0")
    # There should be snapshots
    snaps = sorted(os.listdir(tmp/".envs"/"env2"/"snapshots"))
    assert len(snaps) >= 2
    # The second-last snapshot is after 'a' and before 'b'
    second_last = snaps[-2].split(".")[0]
    mgr.rollback("env2", second_last)
    data = json.loads((tmp/".envs"/"env2"/"env.json").read_text())
    assert "b" not in data["packages"]
    assert data["packages"]["a"] == "1.0"
