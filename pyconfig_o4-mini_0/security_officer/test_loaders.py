import pytest
from config_framework.loaders import register_loader, load, LOADER_REGISTRY

def test_register_and_load():
    def dummy(data): return data.upper()
    register_loader("up", dummy)
    assert "up" in LOADER_REGISTRY
    assert load("up", "abc") == "ABC"

def test_load_missing():
    with pytest.raises(KeyError):
        load("nope", "data")
