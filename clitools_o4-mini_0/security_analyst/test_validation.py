import os
import stat
import pytest
from cli_framework.validation import validate_input

def test_regex():
    assert validate_input("abc123", regex=r"^[a-z0-9]+$")
    with pytest.raises(ValueError):
        validate_input("ABC", regex=r"^[a-z]+$")

def test_file_permissions(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("data")
    os.chmod(str(f), 0o600)
    assert validate_input(str(f), file_permissions=0o600)
    os.chmod(str(f), 0o644)
    with pytest.raises(ValueError):
        validate_input(str(f), file_permissions=0o600)

def test_range():
    assert validate_input("5", range_=(1, 10))
    with pytest.raises(ValueError):
        validate_input("0", range_=(1, 10))
