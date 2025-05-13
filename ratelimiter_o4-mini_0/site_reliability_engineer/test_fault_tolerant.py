import pytest
from rate_limiter.fault_tolerant import ExternalStore, enable_fault_tolerant, local_store

@enable_fault_tolerant
def store_set(store, key, value):
    return store.set(key, value)

@enable_fault_tolerant
def store_get(store, key):
    return store.get(key)

def test_fault_tolerant_with_external_store_up(tmp_path):
    store = ExternalStore(available=True)
    assert store_set(store, "a", 1) is True
    assert store_get(store, "a") == 1

def test_fault_tolerant_with_external_store_down():
    local_store.clear()
    store = ExternalStore(available=False)
    assert store_set(store, "b", 2) is True
    assert store_get(store, "b") == 2
