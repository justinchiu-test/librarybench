import os
import threading
import pytest
from config_manager import ConfigManager, Vault

def test_interpolate_env():
    os.environ['TEST_VAR'] = 'hello'
    cm = ConfigManager()
    result = cm.interpolate("Value is ${ENV:TEST_VAR}")
    assert result == "Value is hello"

def test_interpolate_vault():
    vault = Vault({'secret_key': 's3cr3t'})
    cm = ConfigManager(vault=vault)
    result = cm.interpolate("Password=${VAULT:secret_key}")
    assert result == "Password=s3cr3t"

def test_merge_configs_and_section():
    c1 = {'service': {'api': {'port': 80}, 'worker': {'replicas': 2}}}
    c2 = {'service': {'api': {'port': 8080}, 'new': {'enabled': True}}}
    cm = ConfigManager()
    merged = cm.merge_configs(c1, c2)
    assert merged['service']['api']['port'] == 8080
    assert merged['service']['worker']['replicas'] == 2
    assert cm.section('service.api')['port'] == 8080
    assert cm.section('service.new')['enabled'] is True

def test_diff():
    cm = ConfigManager({'a': 1, 'b': 2})
    other = {'a': 1, 'b': 3}
    d = cm.diff(other)
    assert '-  "b": 2' in d
    assert '+  "b": 3' in d

def test_getters_and_access_hooks():
    cm = ConfigManager({'x': {'i': '10', 's': 'text', 'b1': True, 'b2': 'false'}})
    assert cm.get_int('x.i') == 10
    assert cm.get_str('x.s') == 'text'
    assert cm.get_bool('x.b1') is True
    assert cm.get_bool('x.b2') is False
    with pytest.raises(TypeError):
        cm.get_int('x.s')

def test_validate_schema_and_validator():
    schema = {
        "type": "object",
        "properties": {
            "port": {"type": "integer", "minimum": 1},
            "host": {"type": "string"}
        },
        "required": ["port", "host"]
    }
    cm = ConfigManager({'port': 8080, 'host': 'localhost'})
    # should pass
    cm.validate_schema(schema)
    # register a custom validator
    def no_localhost(cfg):
        if cfg.get('host') == 'localhost':
            raise ValueError("host cannot be localhost")
    cm.register_validator(no_localhost)
    with pytest.raises(ValueError):
        cm.validate_schema(schema)

def test_on_access_and_on_load_hooks():
    cfg = {'liveness': {'path': '/health', 'timeout': 5}}
    cm = ConfigManager(cfg)
    # on_load hook modifies a flag
    flag = {}
    def load_hook(c):
        flag['loaded'] = True
    cm.on_load('liveness', load_hook)
    cm.merge_configs(cfg)  # triggers load
    assert flag.get('loaded') is True
    # on_access hook enforces non-empty path
    def access_hook(c):
        if not c.get('path'):
            raise ValueError("empty path")
    cm.on_access('liveness', access_hook)
    # valid access
    sect = cm.section('liveness')
    assert sect['path'] == '/health'
    # invalidate and test
    cm._config['liveness']['path'] = ''
    with pytest.raises(ValueError):
        cm.section('liveness')

def test_generate_docs_markdown_and_html():
    cfg = {'a': 1, 'nested': {'b': 'x'}}
    cm = ConfigManager(cfg)
    md = cm.generate_docs(markdown=True)
    assert "# Config Reference" in md
    assert "- **a**: int" in md
    html = cm.generate_docs(markdown=False)
    assert "<h1>Config Reference</h1>" in html

def test_register_validator_and_merge():
    cfg = {'port': 22}
    cm = ConfigManager(cfg)
    def no_22(cfg):
        if cfg.get('port') == 22:
            raise ValueError("port 22 is not allowed")
    cm.register_validator(no_22)
    # should raise due to custom validator
    with pytest.raises(ValueError):
        cm.validate_schema({"type": "object", "properties": {"port": {"type": "integer"}}})
    # merge new config without port 22
    new_cfg = {'port': 80}
    cm.merge_configs(new_cfg)
    # now validate should pass
    cm.validate_schema({"type": "object", "properties": {"port": {"type": "integer"}}})

def test_thread_safety():
    cfg = {'value': 100}
    cm = ConfigManager(cfg)
    results = []
    def reader():
        for _ in range(1000):
            x = cm.get('value')
            results.append(x)
    threads = [threading.Thread(target=reader) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert all(r == 100 for r in results)
