import os
import pytest
from adapters.opensource_maintainer.osscli.secrets import fetch_secret

def test_fetch_secret_env(monkeypatch):
    monkeypatch.setenv("MYKEY", "val")
    assert fetch_secret(backend="env", key="MYKEY") == "val"
    assert fetch_secret(backend="env", key="NO") is None

def test_fetch_secret_file(tmp_path):
    f = tmp_path / "s.txt"
    f.write_text("secret\n")
    assert fetch_secret(backend="file", path=str(f)) == "secret"
    with pytest.raises(ValueError):
        fetch_secret(backend="file")
    with pytest.raises(ValueError):
        fetch_secret(backend="unknown")