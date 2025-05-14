import pytest
from scheduler.persistence import (
    PersistenceBackend, ShelveBackend, RedisBackend, SQLiteBackend
)

def test_persistence_interface_load():
    with pytest.raises(NotImplementedError):
        PersistenceBackend().load()

def test_persistence_interface_save():
    with pytest.raises(NotImplementedError):
        PersistenceBackend().save({})

def test_shelve_backend():
    backend = ShelveBackend("test.db")
    data = backend.load()
    assert isinstance(data, dict)
    assert backend.save({"key": "value"}) is None

def test_redis_backend():
    backend = RedisBackend("redis://localhost")
    assert isinstance(backend.load(), dict)
    assert backend.save({"x": 1}) is None

def test_sqlite_backend():
    backend = SQLiteBackend("state.sqlite")
    assert isinstance(backend.load(), dict)
    assert backend.save({"y": 2}) is None
