import pytest
from backend_dev.microcli.version import bump_version

def test_bump_normal():
    assert bump_version("1.2.3") == "1.2.4"

def test_bump_missing_patch():
    assert bump_version("1.0") == "1.0.1"

def test_invalid_format():
    with pytest.raises(ValueError):
        bump_version("a.b.c")
