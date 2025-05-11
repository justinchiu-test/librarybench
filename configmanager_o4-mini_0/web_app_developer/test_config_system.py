import os
import json
import tempfile
import logging
import pytest
from config_system import (
    register_plugin, load_plugin, validate_config,
    export_to_env, get_namespace, snapshot,
    load_toml_source, diff_changes, override_config,
    parse_cli_args, _manager
)

def test_register_and_load_plugin(caplog):
    caplog.set_level(logging.INFO)
    def loader():
        return {'tenant': {'A': {'setting': 1}}}
    called = {}
    def callback(conf):
        called['ok'] = True
    register_plugin('test', loader, callback)
    new = load_plugin('test')
    assert new == {'tenant': {'A': {'setting': 1}}}
    # verify callback was called
    assert called.get('ok') is True
    # verify config inside manager
    assert get_namespace('tenant.A')['setting'] == 1
    # log contains plugin_loaded
    assert any('plugin_loaded' in rec.message for rec in caplog.records)

def test_validate_config_success_and_failure():
    # set up config
    override_config(None, {'features': {'beta': True, 'num': 5}})
    schema = {'features': {'beta': bool, 'num': int}}
    # should validate when providing schema
    assert validate_config(None, {'features': {'beta': False, 'num': 2}}, schema) is True
    # store schema under namespace ''
    assert validate_config('features', get_namespace('features'), {'beta': bool, 'num': int}) is True
    # failure
    with pytest.raises(ValueError):
        validate_config('features', {'beta': 'no', 'num': 2}, {'beta': bool, 'num': int})

def test_export_to_env_and_strings(tmp_path):
    override_config(None, {'a': 1, 'nested': {'b': 'x'}})
    lines = export_to_env(as_string=True, prefix='TEST')
    expected = {'TEST_A=1', 'TEST_NESTED_B=x'}
    assert set(lines) == expected
    # test setting os.environ
    export_to_env(as_string=False, prefix='RUN')
    assert os.environ.get('RUN_A') == '1'
    assert os.environ.get('RUN_NESTED_B') == 'x'

def test_get_namespace_errors():
    override_config(None, {'x': {'y': 2}})
    with pytest.raises(KeyError):
        get_namespace('x.z')
    with pytest.raises(KeyError):
        get_namespace('not.exist')

def test_snapshot_immutable():
    override_config(None, {'foo': {'bar': 10}})
    snap = snapshot()
    assert snap['foo']['bar'] == 10
    with pytest.raises(TypeError):
        snap['foo']['bar'] = 20
    with pytest.raises(TypeError):
        snap['new'] = {}

def test_load_toml_source(tmp_path):
    content = "value = 123\n[inner]\nkey = 'abc'\n"
    f = tmp_path / "test.toml"
    f.write_text(content)
    data = load_toml_source(str(f))
    assert data['value'] == 123
    assert data['inner']['key'] == 'abc'

def test_diff_changes_simple():
    old = {'a': {'x': 1}, 'b': 2}
    new = {'a': {'x': 2}, 'b': 2, 'c': 3}
    diffs = diff_changes(old, new)
    assert diffs == {'a_x': (1, 2), 'c': (None, 3)}

def test_override_config():
    override_config(None, {'m': {'n': 5}})
    # override single key
    changes = override_config('m.n', 7)
    assert changes.get('m_n') == (5, 7)
    assert get_namespace('m')['n'] == 7
    # full override
    changes2 = override_config(None, {'x': 1})
    assert 'm_n' in changes2  # removed
    assert get_namespace('x') == 1

def test_parse_cli_args():
    args = ['--port', '8080', '--feature_flag=True', '--feature_beta']
    res = parse_cli_args(args)
    assert res['port'] == 8080
    assert res['feature_flag'] is True
    assert res['feature_beta'] is True

def test_log_event_structure(caplog):
    caplog.set_level(logging.INFO)
    from config_system import log_event
    log_event('test_event', {'k': 'v'})
    entry = json.loads(caplog.records[-1].message)
    assert entry['event'] == 'test_event'
    assert entry['data'] == {'k': 'v'}
