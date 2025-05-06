import os
import sys
import json
import pytest
import IT_Admin.cli
from IT_Admin.env_manager import EnvironmentManager
from IT_Admin.repository import RepositoryManager

@pytest.fixture
def home(tmp_path, monkeypatch):
    # Set ENV_MANAGER_HOME
    path = tmp_path / "home"
    monkeypatch.setenv("ENV_MANAGER_HOME", str(path))
    return path

@pytest.fixture
def repo_file(tmp_path):
    # Create a simple repo JSON
    data = {"pkg1": ["1.0.0", "2.0.0"]}
    path = tmp_path / "repo.json"
    with open(path, "w") as f:
        json.dump(data, f)
    return str(path)

def run_cmd(monkeypatch, args):
    # Simulate sys.argv and run cli.main()
    monkeypatch.setattr(sys, "argv", args)
    try:
        cli.main()
        return 0
    except SystemExit as e:
        return e.code

def capture_output(monkeypatch, capsys, args):
    code = run_cmd(monkeypatch, args)
    captured = capsys.readouterr()
    return code, captured.out, captured.err

def test_cli_env_and_repo(home, tmp_path, monkeypatch, capsys):
    # Create a JSON env file
    env_file = tmp_path / "e.json"
    data = {"pkg1": ">=1.0"}
    with open(env_file, "w") as f:
        json.dump(data, f)
    # Import
    code, out, err = capture_output(
        monkeypatch, capsys, ["prog", "env", "import", "--file", str(env_file)]
    )
    assert code == 0
    assert "Imported environment 'e'." in out
    # List
    code, out, err = capture_output(
        monkeypatch, capsys, ["prog", "env", "list"]
    )
    assert "e" in out.splitlines()
    # Delete
    code, out, err = capture_output(
        monkeypatch, capsys, ["prog", "env", "delete", "e"]
    )
    assert "Deleted environment 'e'." in out

    # Repo add
    code, out, err = capture_output(
        monkeypatch, capsys, ["prog", "repo", "add", "r1", "/tmp"]
    )
    assert "Added repository 'r1'." in out
    # Repo list
    code, out, err = capture_output(
        monkeypatch, capsys, ["prog", "repo", "list"]
    )
    assert "r1: /tmp" in out
    # Repo remove
    code, out, err = capture_output(
        monkeypatch, capsys, ["prog", "repo", "remove", "r1"]
    )
    assert "Removed repository 'r1'." in out

def test_cli_install(home, repo_file, monkeypatch, capsys):
    # Add repo
    rm = RepositoryManager()
    rm.add_repository("local", repo_file)
    # Create env
    em = EnvironmentManager()
    em.create_environment("test", {"pkg1": ">=1.0"})
    code, out, err = capture_output(
        monkeypatch, capsys,
        ["prog", "install", "--env", "test"]
    )
    assert code == 0
    assert "pkg1==2.0.0" in out.strip()

def test_cli_install_conflict(home, tmp_path, monkeypatch, capsys):
    # No repos added
    em = EnvironmentManager()
    em.create_environment("test", {"pkg1": ">=1.0"})
    code, out, err = capture_output(
        monkeypatch, capsys,
        ["prog", "install", "--env", "test"]
    )
    assert code != 0
    assert "Conflict" in err

def test_cli_install_offline(home, tmp_path, monkeypatch, capsys):
    rm = RepositoryManager()
    # Add a bad remote
    rm.add_repository("remote", "/does/not/exist")
    # Add a valid local
    data = {"pkgA": ["1.0.0"]}
    repo_local = tmp_path / "repo2.json"
    with open(repo_local, "w") as f:
        json.dump(data, f)
    rm.add_repository("local", str(repo_local))
    em = EnvironmentManager()
    em.create_environment("env", {"pkgA": "==1.0.0"})
    code, out, err = capture_output(
        monkeypatch, capsys,
        ["prog", "install", "--env", "env", "--offline"]
    )
    assert code == 0
    assert "pkgA==1.0.0" in out.strip()
