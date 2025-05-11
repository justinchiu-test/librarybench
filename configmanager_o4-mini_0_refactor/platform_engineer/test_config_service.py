import os
import time
import threading
import pytest
import logging
import json
from config_service import ConfigService

def test_register_plugin_and_merge():
    svc = ConfigService()
    svc.load_global_config({'a': 1, 'b': 2})
    svc.load_tenant_config('t1', {'b': 20, 'c': 30})
    def plugin1(tenant):
        return {'c': 300, 'd': 400}
    svc.register_plugin('plugin1', plugin1)
    merged = svc.merge_configs('t1')
    assert merged['a'] == 1
    assert merged['b'] == 20
    # plugin runs before tenant by default precedence
    assert merged['c'] == 30
    # plugin1 extra key
    assert merged['d'] == 400

def test_set_precedence():
    svc = ConfigService()
    svc.load_global_config({'x': 1})
    svc.load_tenant_config('t1', {'x': 10})
    def plugin1(tenant):
        return {'x': 100}
    svc.register_plugin('plugin1', plugin1)
    svc.set_precedence(['plugin', 'global', 'tenant'])
    merged = svc.merge_configs('t1')
    # plugin first, then global (overrides plugin), then tenant (final)
    assert merged['x'] == 10

def test_select_profile():
    svc = ConfigService()
    svc.load_global_config({'k': 'v0'})
    svc.load_tenant_config('t1', {'k': 'v1'})
    svc.select_profile('p1', {'k': 'v2', 'p': 'pv'})
    svc.set_precedence(['global', 'tenant', 'profile'])
    merged = svc.merge_configs('t1')
    assert merged['k'] == 'v2'
    assert merged['p'] == 'pv'

def test_export_to_ini():
    svc = ConfigService()
    svc.load_global_config({'i': '1', 'j': '2'})
    ini = svc.export_to_ini('tX')
    assert '[DEFAULT]' in ini
    assert 'i = 1' in ini
    assert 'j = 2' in ini

def test_export_env_vars(tmp_path, monkeypatch):
    svc = ConfigService()
    svc.load_global_config({'E1': 'V1', 'E2': 'V2'})
    # clear env
    monkeypatch.delenv('E1', raising=False)
    monkeypatch.delenv('E2', raising=False)
    svc.export_env_vars('tX')
    assert os.environ.get('E1') == 'V1'
    assert os.environ.get('E2') == 'V2'

def test_hot_reload_and_callbacks():
    svc = ConfigService()
    svc.load_global_config({'foo': 'bar'})
    results = {}
    def cb(tenant, config):
        results[tenant] = config
    svc.enable_hot_reload(cb)
    svc.trigger_reload('T')
    time.sleep(0.1)
    assert 'T' in results
    assert results['T']['foo'] == 'bar'

def test_compute_acl_caching():
    svc = ConfigService()
    first = svc.compute_acl('t1')
    second = svc.compute_acl('t1')
    assert first == 'acl_for_t1'
    assert second == first
    assert svc.get_acl_call_count() == 1
    # new tenant triggers new compute
    svc.compute_acl('t2')
    assert svc.get_acl_call_count() == 2

def test_fetch_secret_via_plugin():
    svc = ConfigService()
    def secret_plugin(tenant):
        return {'s': f'secret_{tenant}'}
    svc.register_plugin('vault', secret_plugin)
    sec = svc.fetch_secret('vault', 't9')
    assert sec['s'] == 'secret_t9'

def test_setup_logging_custom_handler():
    svc = ConfigService()
    log_msgs = []
    class ListHandler(logging.Handler):
        def emit(self, record):
            log_msgs.append(record.getMessage())
    handler = ListHandler()
    formatter = logging.Formatter('%(levelname)s:%(message)s')
    logger = svc.setup_logging(handler=handler, formatter=formatter)
    logger.info('hello')
    assert any('INFO:hello' in m for m in log_msgs)

def test_merge_logs_structured_json(caplog):
    svc = ConfigService()
    caplog.set_level(logging.INFO)
    svc.load_global_config({'k': 'v'})
    merged = svc.merge_configs('t0')
    # last log entry should be JSON with event merge
    entries = [json.loads(r.message) for r in caplog.records if 'merge' in r.message]
    assert any(e.get('event') == 'merge' and e.get('tenant') == 't0' for e in entries)
