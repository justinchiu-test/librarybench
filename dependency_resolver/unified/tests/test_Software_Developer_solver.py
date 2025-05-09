import pytest
from repo_manager import RepositoryManager
from solver import DependencySolver

@pytest.fixture
def rm(tmp_path, monkeypatch):
    cfg = str(tmp_path / "repos.json")
    return RepositoryManager(config_file=cfg)

def test_solve_single(rm):
    rm.add_repo("r", {"pkg": ["1.0", "2.0", "1.5"]})
    ds = DependencySolver(rm)
    # pick highest
    res = ds.solve({"pkg": ">=1.0"})
    assert res == {"pkg": "2.0"}

def test_solve_constraints(rm):
    rm.add_repo("r", {"p": ["0.1", "0.5", "1.0", "2.0", "2.5"]})
    ds = DependencySolver(rm)
    # between
    res = ds.solve({"p": ">=0.5, <2.5"})
    assert res == {"p": "2.0"}
    # exact
    res2 = ds.solve({"p": "==1.0"})
    assert res2 == {"p": "1.0"}
    # no match
    with pytest.raises(ValueError):
        ds.solve({"p": ">3.0"})
    # missing pkg
    with pytest.raises(KeyError):
        ds.solve({"x": ">=0.1"})

def test_multiple_pkgs(rm):
    rm.add_repo("r1", {"a": ["1.0"], "b": ["0.1", "0.2"]})
    rm.add_repo("r2", {"b": ["1.0"], "c": ["3.0"]})
    ds = DependencySolver(rm)
    res = ds.solve({"a": ">=0.0", "b": ">=0.2", "c": "==3.0"})
    assert res == {"a":"1.0","b":"1.0","c":"3.0"}
