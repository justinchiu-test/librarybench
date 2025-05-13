import os
import json
import base64
import warnings
import tempfile
import pytest
from configlib import (
    ConfigError, SecretManager, JSONSchemaSupport, DeprecationWarnings,
    ConfigMerger, InteractiveCLI, ListMergeStrategies, DocumentationGen,
    CustomFormatLoaders, SecretDecryption, ErrorReporting
)

def test_secret_manager_fetch_and_rotate():
    sm = SecretManager()
    assert sm.fetch_secret("aws", "id123") == "fetched-aws-id123"
    assert sm.rotate_secret("vault", "sec456") == "rotated-vault-sec456"

def test_json_schema_export_and_validate():
    schema = {
        "type": "object",
        "required": ["a", "b"],
        "properties": {
            "a": {"type": "string"},
            "b": {"type": "number"},
            "c": {"type": "array"}
        }
    }
    js = JSONSchemaSupport()
    exported = js.export_schema(schema)
    parsed = json.loads(exported)
    assert parsed == schema
    # valid config
    cfg = {"a": "hello", "b": 3}
    assert js.validate_schema(cfg, schema) is True
    # missing required
    with pytest.raises(ConfigError):
        js.validate_schema({"a": "x"}, schema)
    # wrong type
    with pytest.raises(ConfigError):
        js.validate_schema({"a": "hi", "b": "notnum"}, schema)

def test_deprecation_warnings():
    dw = DeprecationWarnings()
    with pytest.warns(DeprecationWarning) as record:
        dw.warn(["old"], {"old": "new"})
    assert "old is deprecated" in str(record[0].message)

def test_config_merger():
    cm = ConfigMerger()
    os.environ["X"] = "envval"
    d1 = {"a": 1, "b": 2}
    d2 = {"b": 3, "c": 4}
    merged = cm.merge(d1, d2)
    assert merged == {"a":1, "b":3, "c":4}
    merged_env = cm.merge(d1, {}, env_precedence=True)
    assert merged_env["X"] == "envval"

def test_interactive_cli(monkeypatch):
    ic = InteractiveCLI()
    cfg = {"a": "exist"}
    # simulate input for missing key 'b'
    monkeypatch.setattr('builtins.input', lambda prompt: "valb")
    out = ic.prompt_missing(cfg, ["a", "b"])
    assert out["a"] == "exist"
    assert out["b"] == "valb"

def test_list_merge_strategies():
    lms = ListMergeStrategies()
    lists = [[1,2], [2,3]]
    assert lms.merge(lists, "append") == [1,2,2,3]
    assert lms.merge(lists, "replace") == [2,3]
    assert lms.merge(lists, "unique") == [1,2,3]

def test_documentation_gen():
    schema = {
        "properties": {
            "x": {"type": "string", "description": "desc x"},
            "y": {"type": "number", "description": "desc y"}
        }
    }
    dg = DocumentationGen()
    md = dg.generate(schema, "markdown")
    assert "- **x** (string): desc x" in md
    html = dg.generate(schema, "html")
    assert "<ul>" in html and "</ul>" in html

def test_custom_format_loaders(tmp_path):
    cfg = {"foo": "bar"}
    def toml_loader(s):  # dummy loader expecting JSON
        return json.loads(s)
    cfl = CustomFormatLoaders()
    cfl.register("toml", toml_loader)
    file = tmp_path / "test.toml"
    file.write_text(json.dumps(cfg))
    loaded = cfl.load(str(file))
    assert loaded == cfg
    # test fallback JSON
    jf = tmp_path / "test.json"
    jf.write_text(json.dumps(cfg))
    loaded2 = cfl.load(str(jf))
    assert loaded2 == cfg

def test_secret_decryption():
    sd = SecretDecryption()
    # ENC() pattern
    raw = base64.b64encode(b"secret").decode()
    enc = f"ENC({raw})"
    assert sd.decrypt(enc) == "secret"
    # auto base64
    auto = raw
    assert sd.decrypt(auto) == "secret"
    # not base64
    assert sd.decrypt("plain") == "plain"
    # invalid ENC
    with pytest.raises(ConfigError):
        sd.decrypt("ENC(bad@@)")

def test_error_reporting():
    er = ErrorReporting()
    out = er.report("f.py", 10, "line content", "something broke")
    assert "f.py:10:" in out
    assert "something broke" in out
    assert "^" in out
