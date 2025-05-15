from ops_engineer.cli_toolkit.scaffold import gen_scaffold

def test_gen_setup_py():
    s = gen_scaffold("projname", use_poetry=False)
    assert "setup(" in s
    assert "name='projname'" in s

def test_gen_pyproject_toml():
    s = gen_scaffold("myproj", use_poetry=True)
    assert "[tool.poetry]" in s
    assert 'name = "myproj"' in s
