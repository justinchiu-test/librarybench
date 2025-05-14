import pytest
from static_site_engine import auto_reload

def test_auto_reload_calls_callback():
    calls = []
    def cb(path):
        calls.append(path)
    paths = ["a.md", "b.html"]
    auto_reload(paths, cb)
    assert calls == paths
