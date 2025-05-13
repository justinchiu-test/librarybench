import pytest
import tempfile
import os
import json
import base64
import warnings
from config_toolkit import (
    load_yaml, load_xml, load_url, decrypt_token, get_secret,
    merge_configs, warn_deprecated, validate_config, export_json_schema,
    prompt_missing, generate_docs, ConfigError
)
import yaml
import requests

class DummyResponse:
    def __init__(self, text, status_code=200, headers=None):
        self.text = text
        self.status_code = status_code
        self.headers = headers or {"Content-Type": "application/json"}
    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.HTTPError(f"Status {self.status_code}")
    def json(self):
        return json.loads(self.text)

def test_load_yaml_success():
    data = {'a': 1, 'b': {'c': 2}}
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        yaml.dump(data, f)
        path = f.name
    loaded = load_yaml(path)
    assert loaded == data
    os.unlink(path)

def test_load_yaml_error():
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write("a: [1, 2")  # malformed
        path = f.name
    with pytest.raises(ConfigError) as exc:
        load_yaml(path)
    assert "YAML parse error" in str(exc.value)
    os.unlink(path)

def test_load_xml_success():
    content = "<root><a>1</a><b>text</b></root>"
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write(content)
        path = f.name
    loaded = load_xml(path)
    assert loaded == {'a': '1', 'b': 'text'}
    os.unlink(path)

def test_load_xml_error():
    content = "<root><a>1</b></root>"
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write(content)
        path = f.name
    with pytest.raises(ConfigError) as exc:
        load_xml(path)
    assert "XML parse error" in str(exc.value)
    os.unlink(path)

def test_load_url_json(monkeypatch):
    url = "http://example.com"
    data = {'x': 5}
    dummy = DummyResponse(json.dumps(data), headers={"Content-Type": "application/json"})
    monkeypatch.setattr(requests, "get", lambda u: dummy)
    loaded = load_url(url)
    assert loaded == data

def test_load_url_yaml(monkeypatch):
    url = "http://example.com"
    y = yaml.dump({'y': 10})
    dummy = DummyResponse(y, headers={"Content-Type": "text/plain"})
    monkeypatch.setattr(requests, "get", lambda u: dummy)
    loaded = load_url(url)
    assert loaded == {'y': 10}

def test_load_url_error(monkeypatch):
    url = "http://example.com"
    def bad_get(u):
        raise requests.RequestException("fail")
    monkeypatch.setattr(requests, "get", bad_get)
    with pytest.raises(ConfigError):
        load_url(url)

def test_decrypt_token_success():
    original = "secret"
    token = base64.b64encode(original.encode()).decode()
    assert decrypt_token(token) == original

def test_decrypt_token_error():
    with pytest.raises(ConfigError):
        decrypt_token("!!notbase64!!")

def test_get_secret(monkeypatch):
    class DummyClient:
        def get_secret_value(self, SecretId):
            return {'SecretString': 'mysecret'}
    monkeypatch.setattr(boto3, "client", lambda svc: DummyClient())
    assert get_secret("id") == "mysecret"

def test_merge_configs_unique():
    defaults = {'a': 1, 'lst': [1,2]}
    exp = {'b': 2, 'lst': [2,3]}
    env = {'lst': [3,4]}
    merged = merge_configs(defaults, exp, env, list_strategy='unique')
    assert merged['a'] == 1
    assert merged['b'] == 2
    assert merged['lst'] == [1,2,3,4]

def test_merge_configs_replace():
    defaults = {'lst': [1,2]}
    exp = {'lst': [3,4]}
    env = {}
    merged = merge_configs(defaults, exp, env, list_strategy='replace')
    assert merged['lst'] == [3,4]

def test_warn_deprecated():
    cfg = {'old': 5}
    dep = {'old': 'new'}
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        out = warn_deprecated(cfg, dep)
        assert 'new' in out and 'old' not in out
        assert len(w) == 1

def test_validate_config_success():
    cfg = {'x': 1}
    schema = {'type': 'object', 'properties': {'x': {'type': 'number'}}, 'required': ['x']}
    validate_config(cfg, schema)

def test_validate_config_error():
    cfg = {'x': 'a'}
    schema = {'type': 'object', 'properties': {'x': {'type': 'number'}}, 'required': ['x']}
    with pytest.raises(ConfigError) as exc:
        validate_config(cfg, schema)
    assert "Schema validation error" in str(exc.value)

def test_export_json_schema():
    schema = {'a':1}
    out = export_json_schema(schema)
    assert json.loads(out) == schema

def test_prompt_missing(monkeypatch):
    cfg = {'a': None}
    monkeypatch.setattr('builtins.input', lambda prompt: 'value')
    out = prompt_missing(cfg, ['a'])
    assert out['a'] == 'value'

def test_generate_docs():
    cfg = {'a':1, 'b':{'c':2}}
    md = generate_docs(cfg)
    assert "a" in md and "b.c" in md

def test_ConfigError_str():
    err = ConfigError("msg", file="f.py", line=10, context="ctx")
    s = str(err)
    assert "msg" in s and "f.py" in s and "10" in s and "ctx" in s
