import pytest
from ops_engineer.cli_toolkit.version import bump_version

def test_bump_with_existing_tags():
    tags = ["v0.0.1", "v0.0.2", "v1.2.3"]
    assert bump_version(tags) == "v1.2.4"

def test_bump_with_no_valid_tags():
    assert bump_version(["abc", "1.2.3"]) == "v0.0.1"

def test_bump_empty_list():
    assert bump_version([]) == "v0.0.1"
