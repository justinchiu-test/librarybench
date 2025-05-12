import os
import json
from opensource_maintainer.osscli.config import load_config
def test_load_config(tmp_path, monkeypatch):
    ini = tmp_path / "config.ini"
    ini.write_text("[section]\nkey=val\n")
    js = tmp_path / "config.json"
    js.write_text(json.dumps({"a":1}))
    monkeypatch.setenv("OSS_new", "nv")
    conf = load_config([str(ini), str(js)])
    assert conf["section"]["key"] == "val"
    assert conf["a"] == 1
    assert conf["new"] == "nv"
    monkeypatch.delenv("OSS_new", raising=False)
