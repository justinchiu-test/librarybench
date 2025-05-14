import os
import sys
import time
import json
import asyncio
import tempfile
import subprocess
import threading
import pytest
from retry_toolkit import (
    BackoffRegistry, ConfigLoader, StopConditionInterface,
    CancellationPolicy, RetryHistoryCollector, CircuitBreaker,
    retry, async_retry, retry_scope
)

def test_backoff_registry():
    assert BackoffRegistry.get('exponential')(0) == 1
    assert BackoffRegistry.get('exponential')(2) == 4
    assert BackoffRegistry.get('linear')(5) == 5
    BackoffRegistry.register('const', lambda n: 42)
    assert BackoffRegistry.get('const')(10) == 42
    with pytest.raises(KeyError):
        BackoffRegistry.get('unknown')

def test_config_loader_json(tmp_path):
    data = {'a': 1, 'b': 'test'}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(data))
    loaded = ConfigLoader.load_config(str(p))
    assert loaded == data

def test_config_loader_toml(tmp_path):
    if not hasattr(ConfigLoader, 'load_config'):
        pytest.skip("TOML support not available")
    if ConfigLoader.load_config.__qualname__:
        pass
    toml_data = "x = 10\ny = 'hi'\n"
    p = tmp_path / "config.toml"
    p.write_text(toml_data)
    loaded = ConfigLoader.load_config(str(p))
    assert loaded['x'] == 10
    assert loaded['y'] == 'hi'

class MyStopCondition(StopConditionInterface):
    def should_stop(self, exception):
        return isinstance(exception, ValueError)

def test_retry_with_stop_condition():
    collector = RetryHistoryCollector()
    stop = MyStopCondition()
    attempts = {'count': 0}
    @retry(attempts=5, backoff='const', stop_conditions=[stop], history_collector=collector)
    def f():
        attempts['count'] += 1
        raise ValueError("stop now")
    with pytest.raises(ValueError):
        f()
    # Should stop at first because stop condition triggers
    assert attempts['count'] == 1
    assert len(collector.entries) == 1

def test_cancellation_policy():
    cancel = CancellationPolicy()
    @retry(attempts=3, backoff='const', cancellation_policy=cancel)
    def f():
        time.sleep(0.1)
        return "ok"
    # cancel before call
    cancel.cancel()
    with pytest.raises(RuntimeError):
        f()

def test_retry_history_collector_and_backoff():
    collector = RetryHistoryCollector()
    attempts = {'count': 0}
    @retry(attempts=3, backoff='const', history_collector=collector)
    def g():
        attempts['count'] += 1
        if attempts['count'] < 3:
            raise RuntimeError("fail")
        return "success"
    res = g()
    assert res == "success"
    assert attempts['count'] == 3
    # history has 3 entries
    assert len(collector.entries) == 3
    # delays are zero for const backoff
    assert all(e['delay'] == 42 for e in collector.entries)

def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    class Service:
        def __init__(self):
            self.count = 0
        @cb
        def call(self):
            self.count += 1
            raise RuntimeError("bad")
    svc = Service()
    with pytest.raises(RuntimeError):
        svc.call()
    assert cb.state == 'CLOSED'
    with pytest.raises(RuntimeError):
        svc.call()
    # now open
    with pytest.raises(RuntimeError) as excinfo:
        svc.call()
    assert "CircuitOpen" in str(excinfo.value)
    assert cb.state == 'OPEN'
    # wait for recovery
    time.sleep(1.1)
    with pytest.raises(RuntimeError):
        svc.call()
    assert cb.state in ('HALF_OPEN', 'OPEN')

@pytest.mark.asyncio
async def test_async_retry():
    collector = RetryHistoryCollector()
    attempts = {'count': 0}
    @async_retry(attempts=3, backoff='const', history_collector=collector)
    async def af():
        attempts['count'] += 1
        if attempts['count'] < 2:
            raise ValueError("fail")
        return "done"
    res = await af()
    assert res == "done"
    assert attempts['count'] == 2
    assert len(collector.entries) == 2

def test_context_manager_api():
    collector = RetryHistoryCollector()
    with retry_scope(attempts=2, backoff='const', history_collector=collector) as r:
        @r
        def h():
            raise KeyError("x")
    with pytest.raises(KeyError):
        h()
    assert len(collector.entries) == 2

def test_cli_success(tmp_path, monkeypatch, capsys):
    # simulate python cli.py --failures 1 --attempts 2
    script = os.path.abspath('cli.py')
    proc = subprocess.run([sys.executable, script, '--failures', '1', '--attempts', '3'],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    assert 'ok' in proc.stdout

def test_cli_failure(tmp_path):
    script = os.path.abspath('cli.py')
    proc = subprocess.run([sys.executable, script, '--failures', '5', '--attempts', '2'],
                          capture_output=True, text=True)
    assert proc.returncode == 1
    assert 'Error:' in proc.stdout
