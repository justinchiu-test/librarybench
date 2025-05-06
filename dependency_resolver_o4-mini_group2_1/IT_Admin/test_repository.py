import pytest
from IT_Admin.repository import RepositoryManager

@pytest.fixture
def home(tmp_path, monkeypatch):
    path = tmp_path / "home"
    monkeypatch.setenv("ENV_MANAGER_HOME", str(path))
    return path

def test_add_list_remove(home):
    rm = RepositoryManager()
    # Initially empty
    assert rm.list_repositories() == {}
    # Add repo
    rm.add_repository("repo1", "/path/to/repo1")
    repos = rm.list_repositories()
    assert "repo1" in repos and repos["repo1"] == "/path/to/repo1"
    # Duplicate add fails
    with pytest.raises(KeyError):
        rm.add_repository("repo1", "/other")
    # Remove repo
    rm.remove_repository("repo1")
    assert rm.list_repositories() == {}
    # Removing non-existent fails
    with pytest.raises(KeyError):
        rm.remove_repository("repo1")
