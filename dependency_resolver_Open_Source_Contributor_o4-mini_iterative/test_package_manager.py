import os
import json
import pytest
from package_manager import Environment, _compare_versions

def test_version_compare():
    assert _compare_versions("1.0", "1.0") == 0
    assert _compare_versions("1.0", "1.1") < 0
    assert _compare_versions("1.2", "1.1") > 0
    assert _compare_versions("1.0.0", "1") == 0

def test_create_env(tmp_path):
    envdir = tmp_path / "env"
    env = Environment.create_env(str(envdir))
    assert os.path.isdir(str(envdir))
    instf = envdir / "installed.json"
    assert instf.exists()
    with open(instf) as f:
        data = json.load(f)
    assert data == {}

def test_install_remote_latest(tmp_path):
    env = Environment.create_env(str(tmp_path / "e1"))
    env.install("packageA")
    # expect packageA@2.0 and its dep packageB@1.1
    assert env.installed["packageA"] == "2.0"
    assert env.installed["packageB"] == "1.1"
    # reasons
    assert env.reasons["packageA"] == "user"
    assert env.reasons["packageB"] == "packageA"

def test_install_with_constraints(tmp_path):
    env = Environment.create_env(str(tmp_path / "e2"))
    env.install("packageB>=1.0,<1.1")
    assert env.installed == {"packageB": "1.0"}
    # vulnerabilities for B1.0
    vulns = env.check_vulnerabilities()
    assert "packageB" in vulns
    assert "CVE-2020-0001" in vulns["packageB"]

def test_offline_install_success(tmp_path):
    env = Environment.create_env(str(tmp_path / "e3"))
    # packageB@1.0 exists in local only
    env.install("packageB", offline=True)
    assert env.installed["packageB"] == "1.0"

def test_offline_install_fail(tmp_path):
    env = Environment.create_env(str(tmp_path / "e4"))
    with pytest.raises(ValueError):
        env.install("packageA", offline=True)

def test_freeze_and_import(tmp_path):
    env1 = Environment.create_env(str(tmp_path / "e5"))
    env1.install("packageA")
    lock = tmp_path / "lock.json"
    env1.freeze(str(lock))
    # new env
    env2 = Environment.create_env(str(tmp_path / "e6"))
    env2.import_env(str(lock))
    assert env2.installed == env1.installed
    # reasons of imported are user
    for pkg in env2.installed:
        assert env2.reasons[pkg] == "user"

def test_export_alias(tmp_path):
    env1 = Environment.create_env(str(tmp_path / "e7"))
    env1.install("packageC")
    exp = tmp_path / "env_export.json"
    env1.export_env(str(exp))
    with open(exp) as f:
        data = json.load(f)
    assert data == env1.installed

def test_list_updates(tmp_path):
    env = Environment.create_env(str(tmp_path / "e8"))
    # install older version
    env.install("packageB>=1.0,<1.1")
    ups = env.list_updates()
    assert "packageB" in ups
    cur, latest = ups["packageB"]
    assert cur == "1.0"
    assert latest == "1.1"

def test_check_vulnerabilities(tmp_path):
    env = Environment.create_env(str(tmp_path / "e9"))
    env.install("packageA>=2.0,<2.0")  # forces version 2.0
    # That has CVE-2021-0001
    vulns = env.check_vulnerabilities()
    assert vulns["packageA"] == ["CVE-2021-0001"]

def test_explain_chain(tmp_path):
    env = Environment.create_env(str(tmp_path / "e10"))
    env.install("packageC")
    # C->user, A->C, B->A
    chainC = env.explain("packageC")
    assert chainC == ["packageC", "user"]
    chainA = env.explain("packageA")
    assert chainA == ["packageA", "packageC", "user"]
    chainB = env.explain("packageB")
    assert chainB == ["packageB", "packageA", "packageC", "user"]

def test_is_installed(tmp_path):
    env = Environment.create_env(str(tmp_path / "e11"))
    assert not env.is_installed("packageA")
    env.install("packageA")
    assert env.is_installed("packageA")

def test_missing_package(tmp_path):
    env = Environment.create_env(str(tmp_path / "e12"))
    with pytest.raises(ValueError):
        env.install("no_such_pkg")
