import pytest
from microcli.secrets import manage_secrets

def test_manage_ok():
    s = manage_secrets("aws", "key1")
    assert s.startswith("aws:key1")

def test_manage_fail():
    with pytest.raises(ValueError):
        manage_secrets("", "")
