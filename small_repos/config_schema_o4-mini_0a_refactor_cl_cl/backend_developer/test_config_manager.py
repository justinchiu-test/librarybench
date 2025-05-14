import json
from configmanager import ConfigManager, load_config
def test_get_set(tmp_path):
    data = {"one": 1, "two": 2}
    p = tmp_path / "c.json"
    p.write_text(json.dumps(data))
    ConfigManager.load(str(p))
    assert ConfigManager.get("one") == 1
    ConfigManager.set("one", 100)
    assert ConfigManager.get("one") == 100

def test_serialize(tmp_path):
    data = {"x": "y"}
    p = tmp_path / "c2.json"
    p.write_text(json.dumps(data))
    ConfigManager.load(str(p))
    out = ConfigManager.serialize()
    assert out == data
    # original mutation doesn't affect serialized copy
    out["x"] = "z"
    assert ConfigManager.get("x") == "y"
