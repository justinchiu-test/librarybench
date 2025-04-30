import os
import json
import tempfile
import pytest
from env_manager.manager import EnvManager

@pytest.fixture
def mgr(tmp_path, monkeypatch):
    root = tmp_path / "envs"
    monkeypatch.setenv('ENVMGR_ROOT', str(root))
    m = EnvManager()
    return m

def test_env_crud(mgr):
    mgr.create_env("test")
    assert "test" in mgr.list_envs()
    with pytest.raises(FileExistsError):
        mgr.create_env("test")
    mgr.delete_env("test")
    assert "test" not in mgr.list_envs()
    with pytest.raises(FileNotFoundError):
        mgr.delete_env("nope")

def test_install_and_existence(mgr):
    mgr.create_env("e1")
    mgr.install_packages("e1", ["A"])
    # A, B, C should be installed
    for pkg in ["A","B","C"]:
        assert mgr.package_exists("e1", pkg)
    # versions are correct
    inst = mgr._load_installed("e1")
    assert inst["A"]["version"] == "1.0"
    assert inst["B"]["version"] in ["1.0", "1.1"]
    # explain dependency tree
    expl = mgr.explain_dependency("e1", "A")
    # first line A==1.0
    assert expl.splitlines()[0].startswith("A==1.0")

def test_batch_install(mgr):
    mgr.create_env("e2")
    mgr.install_packages("e2", ["C","B"])
    inst = mgr._load_installed("e2")
    assert "B" in inst and "C" in inst

def test_lockfile_export_and_install(mgr, tmp_path):
    mgr.create_env("e3")
    mgr.install_packages("e3", ["B"])
    lock = tmp_path / "lock.json"
    mgr.export_lockfile("e3", str(lock))
    data = json.loads(lock.read_text())
    assert "packages" in data and "B" in data["packages"]
    # new env from lockfile
    mgr.create_env("e4")
    mgr.install_from_lockfile("e4", str(lock))
    inst4 = mgr._load_installed("e4")
    assert inst4["B"]["version"] == data["packages"]["B"]

def test_import_env(mgr, tmp_path):
    mgr.create_env("e5")
    spec = {"packages": ["C"]}
    f = tmp_path / "spec.json"
    f.write_text(json.dumps(spec))
    mgr.import_env("e5", str(f))
    assert mgr.package_exists("e5", "C")

def test_update_notifications(mgr):
    mgr.create_env("e6")
    # default B latest is 1.1, install B at 1.0 by lockfile hack:
    # directly call _install_single
    mgr._install_single("e6", "B", version="1.0")
    notes = mgr.get_update_notifications("e6")
    assert "B" in notes
    assert notes["B"]["latest"] == "1.1"
