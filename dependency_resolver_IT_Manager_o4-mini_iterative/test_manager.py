import pytest
from registry import Registry
from manager import PackageManager

@pytest.fixture
def sample_registry():
    reg = Registry()
    # A depends on B and C
    reg.add_package("C", "1.0.0")
    reg.add_package("B", "1.0.0", dependencies=[("C", "1.0.0")])
    reg.add_package("A", "2.0.0", dependencies=[("B", "1.0.0"), ("C", "1.0.0")])
    # Add updates
    reg.add_package("A", "2.1.0", dependencies=[("B", "1.0.0"), ("C", "1.0.0")])
    reg.add_package("B", "1.1.0", dependencies=[("C", "1.0.0")])
    return reg

def test_install_with_dependencies(sample_registry):
    pm = PackageManager(sample_registry)
    pm.install("A", "2.0.0")
    installed = pm.list_installed()
    # A, B, C should all be installed
    assert set(installed.keys()) == {"A", "B", "C"}
    assert installed["A"] == "2.0.0"
    assert installed["B"] == "1.0.0"
    assert installed["C"] == "1.0.0"

def test_reinstall_same_version_is_idempotent(sample_registry):
    pm = PackageManager(sample_registry)
    pm.install("C", "1.0.0")
    pm.install("C", "1.0.0")  # should not error
    assert pm.list_installed() == {"C": "1.0.0"}

def test_show_metadata(sample_registry):
    pm = PackageManager(sample_registry)
    meta = pm.show_metadata("A", "2.1.0")
    assert meta["name"] == "A"
    assert meta["version"] == "2.1.0"
    assert {"1.0.0", "2.0.0", "2.1.0"} == set(meta["version_history"])
    deps = meta["dependencies"]
    assert {"B", "C"} == {d["name"] for d in deps}

def test_check_updates(sample_registry):
    pm = PackageManager(sample_registry)
    pm.install("A", "2.0.0")
    pm.install("B", "1.0.0")
    updates = pm.check_updates()
    # A has 2.1.0, B has 1.1.0
    assert updates["A"] == ("2.0.0", "2.1.0")
    assert updates["B"] == ("1.0.0", "1.1.0")
    # C has no update
    assert "C" not in updates
