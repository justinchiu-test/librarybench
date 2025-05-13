import os
import time
import tempfile
import pytest
import json
import yaml
from pipeline import (
    MonitoringMetrics, RealTimeLogging, JSONSerialization,
    YAMLSerialization, DataValidation, ErrorHandlingSkip,
    ErrorHandlingRetry, TransientError, CachingStage,
    Batch, Group, Checkpointing, ConfigManager, Pipeline
)

def test_monitoring_metrics():
    m = MonitoringMetrics()
    m.record_trade('AAPL')
    m.record_trade('AAPL')
    m.record_trade('GOOG')
    assert m.get_trade_count('AAPL') == 2
    assert m.get_trade_count('GOOG') == 1
    m.record_latency('op1', 0.5)
    m.record_latency('op1', 0.7)
    assert pytest.approx(m.get_latency('op1'), [0.5, 0.7])

def test_realtime_logging():
    log = RealTimeLogging()
    log.log_event('test')
    logs = log.get_logs()
    assert len(logs) == 1
    assert logs[0]['message'] == 'test'
    assert 'timestamp' in logs[0]

def test_serialization():
    obj = {'a': 1, 'b': 2}
    j = JSONSerialization.serialize(obj)
    assert json.loads(j) == obj
    y = YAMLSerialization.serialize(obj)
    assert yaml.safe_load(y) == obj

def test_data_validation_success_and_failure():
    schema = {'symbol': str, 'price': float}
    dv = DataValidation(schema)
    msg = {'symbol': 'AAPL', 'price': 123.45}
    assert dv.validate(msg) is True
    bad = {'symbol': 'AAPL', 'price': '123.45'}
    with pytest.raises(ValueError):
        dv.validate(bad)

def test_error_handling_skip():
    schema = {'a': int}
    dv = DataValidation(schema)
    skip = ErrorHandlingSkip()
    func = skip.wrap(dv.validate)
    assert func({'a': 1}) is True
    assert func({'a': 'wrong'}) is None
    assert len(skip.quarantine) == 1
    entry = skip.quarantine[0]
    assert entry['message'] == {'a': 'wrong'}
    assert 'expected' in entry['error']

def test_error_handling_retry_success():
    call_count = {'n': 0}
    def flaky(x):
        call_count['n'] += 1
        if call_count['n'] < 2:
            raise TransientError("fail")
        return x * 2
    retry = ErrorHandlingRetry(attempts=3)
    f = retry.wrap(flaky)
    assert f(3) == 6
    assert call_count['n'] == 2

def test_error_handling_retry_failure():
    def always_fail(x):
        raise TransientError("always")
    retry = ErrorHandlingRetry(attempts=2)
    f = retry.wrap(always_fail)
    with pytest.raises(TransientError):
        f(1)

def test_caching_stage():
    cache = CachingStage(maxsize=2)
    cache.set('a', 1)
    cache.set('b', 2)
    assert cache.get('a') == 1
    cache.set('c', 3)
    assert cache.get('b') is None
    assert cache.get('c') == 3

def test_batch_and_group():
    now = time.time()
    msgs = [
        {'timestamp': now, 'symbol': 'A', 'price': 10.0, 'quantity': 1},
        {'timestamp': now + 0.5, 'symbol': 'A', 'price': 12.0, 'quantity': 2},
        {'timestamp': now + 1.5, 'symbol': 'B', 'price': 20.0, 'quantity': 1}
    ]
    batcher = Batch(window_size=1)
    windows = batcher.batch(msgs)
    assert len(windows) == 2
    grp = Group()
    first = grp.process_window(windows[0])
    assert 'A' in first
    assert first['A']['count'] == 2
    assert pytest.approx(first['A']['vwap'], first= (10*1+12*2)/3 )
    second = grp.process_window(windows[1])
    assert 'B' in second and second['B']['count'] == 1

def test_checkpointing(tmp_path):
    state = {'x': 123}
    file = tmp_path / "cp.pkl"
    cp = Checkpointing(str(file))
    cp.save(state)
    loaded = cp.load()
    assert loaded == state

def test_config_manager(tmp_path):
    cfg = {'a': 1, 'b': 'two'}
    file = tmp_path / "cfg.yaml"
    with open(file, 'w') as f:
        yaml.safe_dump(cfg, f)
    cm = ConfigManager(str(file))
    assert cm.get('a') == 1
    assert cm.get('b') == 'two'
    assert cm.get('c', 3) == 3

def test_pipeline_integration():
    # pipeline: validate, skip errors, log, metrics, serialize JSON
    schema = {'symbol': str, 'price': float}
    dv = DataValidation(schema)
    skip = ErrorHandlingSkip()
    rl = RealTimeLogging()
    mm = MonitoringMetrics()
    def record_tools(msg):
        mm.record_trade(msg['symbol'])
        rl.log_event(msg)
        return msg
    stages = [
        skip.wrap(dv.validate),
        lambda msg: msg,  # pass through
        record_tools,
        lambda msg: JSONSerialization.serialize(msg)
    ]
    p = Pipeline(stages)
    good = {'symbol': 'X', 'price': 1.23}
    bad = {'symbol': 'X', 'price': 'nope'}
    out = p.process(good)
    assert isinstance(out, str)
    assert json.loads(out) == good
    assert mm.get_trade_count('X') == 1
    assert len(rl.get_logs()) == 1
    assert p.process(bad) is None
    assert len(skip.quarantine) == 1
