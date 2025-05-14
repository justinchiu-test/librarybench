import os
import tempfile
import shelve
from src.personas.translator.cache import TranslationCache

def test_in_memory_cache():
    c = TranslationCache(use_disk=False)
    assert c.get('x') is None
    c.set('x', 123)
    assert c.get('x') == 123

def test_disk_cache(tmp_path):
    dbfile = tmp_path / 'cache.db'
    c = TranslationCache(cache_dir=str(tmp_path), use_memory=False)
    c.set('a', 'apple')
    assert c.get('a') == 'apple'
    c.close()
    
    # Reopen cache to verify persistence
    c2 = TranslationCache(cache_dir=str(tmp_path), use_memory=False)
    assert c2.get('a') == 'apple'
    c2.close()