import os
from adapters.devops_engineer.devops_cli.init_package import init_package

def test_init_setup(tmp_path):
    content = init_package("mypkg", use_pyproject=False, target_dir=str(tmp_path))
    assert "name=\"mypkg\"" in content
    path = tmp_path / "setup.py"
    assert path.exists()
    assert content == path.read_text()

def test_init_pyproject(tmp_path):
    content = init_package("lib", use_pyproject=True, target_dir=str(tmp_path))
    assert 'name = "lib"' in content
    path = tmp_path / "pyproject.toml"
    assert path.exists()
    assert content == path.read_text()