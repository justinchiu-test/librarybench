import time
import pytest
from iotdb.cache import QueryCache

def test_cache_set_get():
    cache = QueryCache(ttl_seconds=1)
    cache.set('a', 1)
    assert cache.get('a') == 1
    time.sleep(1.1)
    assert cache.get('a') is None
