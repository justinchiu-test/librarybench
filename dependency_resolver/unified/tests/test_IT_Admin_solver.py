import json
import pytest
from solver import DependencySolver, ConflictError

@pytest.fixture
def repo_file(tmp_path):
    # Create a fake repository index JSON
    data = {
        "pkg1": ["1.0.0", "1.2.0", "2.0.0"],
        "pkg2": ["0.5.0", "1.0.0"]
    }
    path = tmp_path / "repo.json"
    with open(path, "w") as f:
        json.dump(data, f)
    return str(path)

def test_solve_success(repo_file):
    solver = DependencySolver([repo_file])
    constraints = {"pkg1": ">=1.0,<2.0", "pkg2": "==1.0.0"}
    plan = solver.solve(constraints)
    assert plan == {"pkg1": "1.2.0", "pkg2": "1.0.0"}

def test_solve_no_package(repo_file):
    solver = DependencySolver([repo_file])
    with pytest.raises(ConflictError):
        solver.solve({"pkgX": ">=1.0"})

def test_solve_no_matching_version(repo_file):
    solver = DependencySolver([repo_file])
    with pytest.raises(ConflictError):
        solver.solve({"pkg2": ">1.0"})
