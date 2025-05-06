import os
import tempfile
from Student.env_manager.cache import CacheManager

def test_cache_fetch(tmp_path):
    cd = tmp_path / "cache"
    cm = CacheManager(cache_dir=str(cd))
    path1 = cm.fetch_package("P", "1.0")
    assert os.path.isfile(path1)
    # fetching again doesn't error, same file
    path2 = cm.fetch_package("P", "1.0")
    assert path1 == path2
