import os
from src.personas.backend_dev.microcli.scaffold import gen_scaffold

def test_gen_setup(tmp_path):
    path = tmp_path / "proj"
    gen_scaffold(str(path), "projname", use_pyproject=False)
    f = path / "setup.py"
    assert f.exists()
    content = f.read_text()
    assert "setup(" in content
    assert "console_scripts" in content

def test_gen_pyproject(tmp_path):
    path = tmp_path / "proj2"
    gen_scaffold(str(path), "proj2", use_pyproject=True)
    f = path / "pyproject.toml"
    assert f.exists()
    content = f.read_text()
    assert "[project]" in content
