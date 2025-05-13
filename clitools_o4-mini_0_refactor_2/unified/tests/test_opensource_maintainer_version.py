import os
from opensource_maintainer.osscli.version import bump_version
def test_bump_version(tmp_path):
    vf = tmp_path / "version.py"
    vf.write_text("__version__ = '1.2.3'\n")
    new = bump_version(str(vf))
    assert new == "1.2.4"
    content = vf.read_text()
    assert "1.2.4" in content
