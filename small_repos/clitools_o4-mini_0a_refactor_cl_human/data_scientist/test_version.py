import os
import tempfile
import pytest
from datapipeline_cli.version import get_version, bump_version, VERSION_FILE

def test_get_version_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    if os.path.exists('version.txt'):
        os.remove('version.txt')
    assert get_version() == '0.0.0'

def test_bump_and_get_version(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with open('version.txt', 'w') as f:
        f.write('1.2.3')
    assert get_version() == '1.2.3'
    new = bump_version()
    assert new == '1.2.4'
    assert get_version() == '1.2.4'

def test_bump_invalid_format(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with open('version.txt', 'w') as f:
        f.write('invalid')
    with pytest.raises(ValueError):
        bump_version()
