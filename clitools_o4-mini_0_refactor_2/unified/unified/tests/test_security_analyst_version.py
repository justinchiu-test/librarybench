import pytest
from adapters.security_analyst.cli_framework.version import bump_version

def test_bump_with_existing_tags():
    tags = ["0.0.1", "0.1.0", "bad", "1.0.0"]
    new = bump_version(tags)
    assert new == "1.0.1"

def test_bump_no_tags():
    new = bump_version([])
    assert new == "0.0.1"