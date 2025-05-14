import json
import time
from backend_developer.configmanager import load_config, _cache

def test_cache_works(tmp_path):
    data = {"x": 10}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(data))
    cfg1 = load_config(str(p))
    before = _cache.copy()
    cfg2 = load_config(str(p))
    assert cfg1 == cfg2
    assert _cache == before

def test_cache_updates_on_change(tmp_path):
    data1 = {"x": 1}
    data2 = {"x": 2}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(data1))
    cfg1 = load_config(str(p))
    time.sleep(0.01)
    p.write_text(json.dumps(data2))
    cfg2 = load_config(str(p))
    assert cfg2["x"] == 2
