import pytest
from registry import Registry, Version, Package

def test_version_equality_and_ordering():
    v1 = Version("1.2.3")
    v2 = Version("1.2.10")
    v3 = Version("1.2.3")
    assert v1 < v2
    assert v2 > v1
    assert v1 == v3
    assert str(v2) == "1.2.10"

def test_invalid_version_string():
    from registry import Version
    with pytest.raises(ValueError):
        Version("1.a.3")
    with pytest.raises(ValueError):
        Version(123)

def test_add_and_get_package():
    reg = Registry()
    reg.add_package("foo", "1.0.0", dependencies=[("bar", "0.1")])
    pkg = reg.get_package("foo", "1.0.0")
    assert pkg.name == "foo"
    assert str(pkg.version) == "1.0.0"
    assert pkg.dependencies == [("bar", "0.1")]

def test_add_duplicate_package_raises():
    reg = Registry()
    reg.add_package("x", "0.1")
    with pytest.raises(ValueError):
        reg.add_package("x", "0.1")

def test_list_versions_and_search():
    reg = Registry()
    versions = ["1.0.0", "1.2.0", "2.0.0"]
    for v in versions:
        reg.add_package("pkg", v)
    assert reg.list_versions("pkg") == ["1.0.0", "1.2.0", "2.0.0"]
    # search by substring
    found = reg.search(name_substr="PK")
    assert all(p.name == "pkg" for p in found)
    # exact version
    exact = reg.search(name_substr="pkg", version_spec="1.2.0")
    assert len(exact) == 1 and str(exact[0].version) == "1.2.0"
    # >= spec
    ge = reg.search(name_substr="pkg", version_spec=">=1.2.0")
    assert set(str(p.version) for p in ge) == {"1.2.0", "2.0.0"}

def test_get_nonexistent_package_raises():
    reg = Registry()
    with pytest.raises(KeyError):
        reg.get_package("nope", "1.0.0")
    reg.add_package("a", "1.0")
    with pytest.raises(KeyError):
        reg.get_package("a", "2.0")
