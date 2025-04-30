import os
import json
import pytest
from env_manager import EnvironmentManager

@pytest.fixture
def home(tmp_path, monkeypatch):
    # Override the home directory for the manager
    path = tmp_path / "home"
    monkeypatch.setenv("ENV_MANAGER_HOME", str(path))
    return path

def test_create_and_get_and_list_and_delete(home):
    em = EnvironmentManager()
    # Initially empty
    assert em.list_environments() == []
    # Create environment
    pkgs = {"pkg1": ">=1.0"}
    em.create_environment("testenv", pkgs)
    assert "testenv" in em.list_environments()
    data = em.get_environment("testenv")
    assert data == pkgs
    # Duplicate creation should fail
    with pytest.raises(FileExistsError):
        em.create_environment("testenv", pkgs)
    # Delete environment
    em.delete_environment("testenv")
    assert em.list_environments() == []
    # Deleting non-existent should fail
    with pytest.raises(FileNotFoundError):
        em.delete_environment("testenv")

def test_import_environment(home, tmp_path):
    em = EnvironmentManager()
    # Prepare a JSON file
    data = {"pkgA": "==2.0"}
    file = tmp_path / "myenv.json"
    with open(file, "w") as f:
        json.dump(data, f)
    name = em.import_environment(str(file))
    assert name == "myenv"
    assert name in em.list_environments()
    assert em.get_environment(name) == data
    # Importing again should fail
    with pytest.raises(FileExistsError):
        em.import_environment(str(file))
