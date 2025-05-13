from pipeline.cache import Cache

def test_cache():
    c = Cache()
    assert c.get('x') is None
    c.set('x', 10)
    assert c.get('x') == 10
