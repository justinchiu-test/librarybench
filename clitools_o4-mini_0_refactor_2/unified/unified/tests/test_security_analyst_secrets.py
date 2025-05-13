import pytest
from adapters.security_analyst.cli_framework.secrets import fetch_secret

def test_fetch_gpg(tmp_path):
    f = tmp_path / "secret.txt"
    f.write_text("topsecret")
    uri = "gpg://" + str(f)
    assert fetch_secret(uri) == "topsecret"

def test_fetch_missing(tmp_path):
    uri = "gpg://" + str(tmp_path / "nofile")
    with pytest.raises(FileNotFoundError):
        fetch_secret(uri)

def test_fetch_kms():
    with pytest.raises(NotImplementedError):
        fetch_secret("kms://id")

def test_fetch_vault():
    with pytest.raises(NotImplementedError):
        fetch_secret("vault://id")