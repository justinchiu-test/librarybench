import os
import tempfile
from pipeline.caching import CachingStage

def test_memory_caching():
    c = CachingStage(cache_type="memory")
    c.set("a", 1)
    assert c.get("a") == 1
    assert c.get("missing") is None
    c.clear()
    assert c.get("a") is None

def test_disk_caching(tmp_path):
    f = tmp_path / "testcache.pkl"
    c = CachingStage(cache_type="disk", cache_file=str(f))
    c.set("k1", "v1")
    c.set("k2", 123)
    assert c.get("k1") == "v1"
    assert c.get("k2") == 123
    c.clear()
    # after clear, file removed
    assert not os.path.exists(str(f))
