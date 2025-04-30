import pytest
from package_manager.registry import Registry, compare_versions
from package_manager.models import Package, Metadata

def test_compare_versions_basic():
    assert compare_versions("1.0.0", "1.0.0") == 0
    assert compare_versions("1.0.1", "1.0.0") == 1
    assert compare_versions("1.0.0", "1.0.1") == -1
    assert compare_versions("1.2.0", "1.10.0") == -1
    assert compare_versions("2.0", "1.9.9") == 1

@pytest.fixture
def registry():
    return Registry()

def test_list_packages(registry):
    packages = registry.list_packages()
    assert "packageA" in packages
    assert "packageB" in packages
    assert "packageC" in packages

def test_list_versions(registry):
    versions = registry.list_versions("packageA")
    assert versions == ["1.0.0", "1.1.0", "2.0.0"]
    assert registry.list_versions("no_such") == []

def test_get_metadata(registry):
    meta = registry.get_metadata("packageA", "1.1.0")
    assert isinstance(meta, Metadata)
    assert meta.version == "1.1.0"
    assert "packageB>=2.0.0" in meta.dependencies
    assert registry.get_metadata("packageA", "9.9.9") is None

def test_search_no_spec(registry):
    # should return latest version per package
    result = registry.search("packageA")
    assert len(result) == 1
    pkg = result[0]
    assert pkg.name == "packageA" and pkg.metadata.version == "2.0.0"

def test_search_exact_version(registry):
    result = registry.search("packageA", "==1.0.0")
    assert len(result) == 1
    assert result[0].metadata.version == "1.0.0"

def test_search_range_version(registry):
    res = registry.search("packageA", ">=1.1.0")
    vers = sorted([p.metadata.version for p in res])
    assert vers == ["1.1.0", "2.0.0"]
    res2 = registry.search("packageA", "<2.0.0")
    vers2 = sorted([p.metadata.version for p in res2])
    assert vers2 == ["1.0.0", "1.1.0"]

def test_search_name_filter(registry):
    # partial, case-insensitive
    res = registry.search("PackageA")
    assert len(res) == 1 and res[0].name == "packageA"
    res_empty = registry.search("zzz")
    assert res_empty == []
