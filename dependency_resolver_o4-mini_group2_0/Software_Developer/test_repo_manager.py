import os
import json
import tempfile
import pytest
from Software_Developer.repo_manager import RepositoryManager

@pytest.fixture
def tmp_config(tmp_path):
    return str(tmp_path / "repos.json")

def test_add_list_remove(tmp_config):
    rm = RepositoryManager(config_file=tmp_config)
    # initially empty
    assert rm.list_repos() == {}
    # add repo
    packages = {"foo": ["1.0", "2.0"], "bar": ["0.1"]}
    rm.add_repo("r1", packages)
    assert "r1" in rm.list_repos()
    assert rm.list_repos()["r1"] == packages
    # duplicate add
    with pytest.raises(ValueError):
        rm.add_repo("r1", packages)
    # remove
    rm.remove_repo("r1")
    assert rm.list_repos() == {}
    # remove missing
    with pytest.raises(KeyError):
        rm.remove_repo("r2")

def test_get_all_packages(tmp_config):
    rm = RepositoryManager(config_file=tmp_config)
    rm.add_repo("rA", {"a": ["1.0", "1.1"], "b": ["2.0"]})
    rm.add_repo("rB", {"a": ["0.9"], "c": ["3.0"]})
    allp = rm.get_all_packages()
    assert set(allp.keys()) == {"a", "b", "c"}
    assert set(allp["a"]) == {"1.0", "1.1", "0.9"}
