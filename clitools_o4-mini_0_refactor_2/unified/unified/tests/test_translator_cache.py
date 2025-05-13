import os
import tempfile
import shelve
import pytest
from adapters.translator.cache import Cache

def test_in_memory_cache():
    c = Cache()
    assert c.get('x') is None
    c.set('x', 123)
    assert c.get('x') == 123

def test_disk_cache(tmp_path):
    dbfile = tmp_path / 'cache.db'
    c = Cache(str(dbfile))
    c.set('a', 'apple')
    assert c.get('a') == 'apple'
    c.close()
    shelf = shelve.open(str(dbfile))
    assert shelf.get('a') == 'apple'
    shelf.close()