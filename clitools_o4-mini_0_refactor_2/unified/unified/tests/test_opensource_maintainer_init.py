import os
from adapters.opensource_maintainer.osscli.init_package import init_package

def test_init_package(tmp_path):
    path = str(tmp_path / "proj")
    result = init_package(path)
    assert result is True
    assert os.path.exists(os.path.join(path, "setup.py"))
    assert os.path.exists(os.path.join(path, ".github", "workflows", "ci.yml"))
    assert os.path.exists(os.path.join(path, "tests", "__init__.py"))