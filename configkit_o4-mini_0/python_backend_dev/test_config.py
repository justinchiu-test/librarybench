import os
import time
import tempfile
import threading
import pytest
from datetime import datetime, timedelta
import config

def setup_function():
    # Reset config between tests
    config._config.clear()
    config._coercers.clear()
    for k in config._hooks:
        config._hooks[k].clear()

def test_load_toml_and_get(tmp_path, monkeypatch):
    if config.toml is None:
        pytest.skip("toml not installed")
    content = """
    [database]
    url = "postgres://user:pass@localhost/db"
    [service]
    port = 8080
    """
    p = tmp_path / "test.toml"
    p.write_text(content)
    cfg = config.load_toml(str(p))
    assert cfg['database']['url'] == "postgres://user:pass@localhost/db"
    assert config.get("service.port") == 8080

def test_load_yaml_and_get(tmp_path):
    if config.yaml is None:
        pytest.skip("yaml not installed")
    content = """
    service:
      name: testsvc
      replicas: 3
    ---
    another: doc
    """
    p = tmp_path / "test.yaml"
    p.write_text(content)
    cfg = config.load_yaml(str(p))
    # single dict merged
    assert config.get("service.name") == "testsvc"
    assert config.get("service.replicas") == 3
    # additional docs stored
    assert 'yaml_docs' in cfg
    assert {'another': 'doc'} in cfg['yaml_docs']

def test_resolve_variables_env_and_ref(monkeypatch):
    config._config.clear()
    os.environ['FOO'] = 'bar'
    config._config['x'] = 'value'
    s = "env is ${FOO} and ref is ${x}"
    out = config.resolve_variables(s)
    assert out == "env is bar and ref is value"

def test_merge_lists_append_and_prepend():
    config._config.clear()
    config._config['middleware'] = ['a', 'b']
    new = config.merge_lists('middleware', ['c'], position='append')
    assert new == ['a', 'b', 'c']
    new2 = config.merge_lists('middleware', ['z'], position='prepend')
    assert new2 == ['z', 'a', 'b', 'c']

def test_set_profile_and_env(monkeypatch):
    if 'PYTHON_ENV' in os.environ:
        del os.environ['PYTHON_ENV']
    prof = config.set_profile('prod')
    assert prof == 'prod'
    assert os.environ['PYTHON_ENV'] == 'prod'
    prof2 = config.set_profile()
    assert prof2 == 'prod'

def test_with_defaults():
    config._config.clear()
    config._config['db'] = {'host': 'localhost'}
    defaults = {'db': {'host': '127.0.0.1', 'port': 5432}, 'cache': {'ttl': 60}}
    cfg = config.with_defaults(defaults)
    assert cfg['db']['host'] == 'localhost'
    assert cfg['db']['port'] == 5432
    assert cfg['cache']['ttl'] == 60

def test_get_default():
    config._config.clear()
    assert config.get('no.such.path', 'def') == 'def'

def test_register_and_run_hooks(tmp_path):
    called_pre = []
    called_post = []
    called_export = []
    def pre(): called_pre.append(True)
    def post(cfg): called_post.append(cfg.copy())
    def exp(cfg): called_export.append(list(cfg.keys()))
    config.register_hook('pre', pre)
    config.register_hook('post', post)
    config.register_hook('export', exp)
    # load yaml triggers pre and post
    if config.yaml:
        p = tmp_path / "h.yaml"
        p.write_text("a: 1")
        config.load_yaml(str(p))
    else:
        # simulate hooks manually
        for h in config._hooks['pre']: h()
        for h in config._hooks['post']: h({'test':1})
    assert called_pre, "pre hook not called"
    assert called_post, "post hook not called"
    # export
    config._config['k'] = 5
    exported = config.export_config()
    assert exported is config._config
    assert called_export, "export hook not called"

def test_register_coercer():
    def to_dt(s): return datetime.fromisoformat(s)
    config.register_coercer('datetime', to_dt)
    assert 'datetime' in config._coercers
    assert config._coercers['datetime']('2020-01-01T00:00:00') == datetime(2020,1,1)

def test_watch_and_reload(tmp_path):
    calls = []
    p = tmp_path / "w.txt"
    p.write_text("v1")
    def cb():
        calls.append(time.time())
    watcher = config.watch_and_reload(str(p), cb, interval=0.01)
    time.sleep(0.02)
    # modify file
    p.write_text("v2")
    time.sleep(0.05)
    assert len(calls) >= 1
    # stop thread by deleting file
    p.unlink()
    time.sleep(0.02)
