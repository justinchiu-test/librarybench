import os
import subprocess
import security_analyst.toml
import pytest
from security_analyst.cli_framework.package import init_package, publish_package

class DummyProc:
    def __init__(self, returncode=0):
        self.returncode = returncode
        self.stdout = b""
        self.stderr = b""

def test_init_package(tmp_path):
    deps = {"requests": "2.25.1"}
    path = init_package(str(tmp_path), "myproj", deps)
    assert os.path.exists(path)
    data = toml.load(path)
    assert data["tool"]["poetry"]["name"] == "myproj"
    assert data["tool"]["poetry"]["dependencies"]["requests"] == "2.25.1"

def test_publish_package(monkeypatch, tmp_path):
    wheel = tmp_path / "pkg-0.1-py3-none.whl"
    asc = tmp_path / "pkg-0.1-py3-none.whl.asc"
    wheel.write_text("wheel")
    asc.write_text("sig")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: DummyProc(0))
    assert publish_package([str(wheel)], "http://repo") is True

def test_publish_package_missing_sig(tmp_path):
    wheel = tmp_path / "pkg.whl"
    wheel.write_text("wheel")
    with pytest.raises(ValueError):
        publish_package([str(wheel)], "http://repo")
