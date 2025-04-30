import json
import os
import tempfile
import pytest
from env_manager.repository import RepositoryManager

@pytest.fixture
def sample_repo(tmp_path):
    data = {
        "X": {"0.1": [], "0.2": []},
        "Y": {"1.0": ["X"]}
    }
    p = tmp_path / "repo.json"
    p.write_text(json.dumps(data))
    return str(p)

def test_default_repo_contains_ABC():
    rm = RepositoryManager()
    # default repo has A, B, C
    assert "A" in rm.list_repos()[0]  # path ends with default_repo.json
    # Check that fetching A works
    versions = rm.get_available_versions("A")
    assert "1.0" in versions
    assert rm.get_latest_version("A") == "1.0"

def test_add_and_remove_repo(sample_repo):
    rm = RepositoryManager()
    before = len(rm.list_repos())
    rm.add_repo(sample_repo)
    assert sample_repo in rm.list_repos()
    assert len(rm.list_repos()) == before + 1
    rm.remove_repo(sample_repo)
    assert sample_repo not in rm.list_repos()

def test_get_package_info_precedence(sample_repo):
    rm = RepositoryManager()
    rm.add_repo(sample_repo)
    # Y is only in sample_repo
    assert rm.get_latest_version("Y") == "1.0"
    # X had 0.2 in sample_repo, default repo does not have X => picks from sample
    assert "0.2" in rm.get_available_versions("X")
