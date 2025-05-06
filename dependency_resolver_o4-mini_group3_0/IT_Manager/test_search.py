import pytest
from IT_Manager.registry import Registry
from IT_Manager.search import search_packages

@pytest.fixture
def reg():
    r = Registry()
    r.add_package("foo", "0.1")
    r.add_package("foo", "0.2")
    r.add_package("bar", "1.0")
    r.add_package("baz", "2.0")
    return r

def test_search_by_name(reg):
    results = search_packages(reg, name="ba")
    names = {r["name"] for r in results}
    assert names == {"bar", "baz"}

def test_search_exact_version(reg):
    results = search_packages(reg, name="foo", version="0.2")
    assert len(results) == 1
    assert results[0]["version"] == "0.2"

def test_search_ge_version(reg):
    results = search_packages(reg, name="foo", version=">=0.2")
    assert len(results) == 1
    assert results[0]["version"] == "0.2"

def test_search_no_match(reg):
    results = search_packages(reg, name="qux")
    assert results == []
