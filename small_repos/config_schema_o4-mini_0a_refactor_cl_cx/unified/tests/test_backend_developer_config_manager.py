import json
from configschema import load_config
def test_get_set(tmp_path):
    data = {"one": 1, "two": 2}
    p = tmp_path / "c.json"
    p.write_text(json.dumps(data))
    cfg = load_config(str(p))
    assert cfg.get("one") == 1
    cfg.set("one", 100)
    assert cfg.get("one") == 100

def test_serialize(tmp_path):
    data = {"x": "y"}
    p = tmp_path / "c2.json"
    p.write_text(json.dumps(data))
    cfg = load_config(str(p))
    out = cfg.serialize()
    assert out == data
    # original mutation doesn't affect serialized copy
    out["x"] = "z"
    assert cfg.get("x") == "y"
