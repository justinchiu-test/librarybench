import time
import pytest
from watcher import Watcher

def test_metrics_endpoint_and_metrics_collection():
    w = Watcher()
    assert not w.metrics_started
    w.start_metrics_endpoint(host='127.0.0.1', port=9000)
    assert w.metrics_started
    assert w.metrics_host == '127.0.0.1'
    assert w.metrics_port == 9000
    # scan once should increment reload count
    result = w.scan_once([])
    assert result == []
    metrics = w.get_metrics()
    assert 'reloads_per_sec' in metrics
    assert 'avg_latency' in metrics
    assert w.reload_count == 1

def test_scan_once_with_ignore_and_filters():
    w = Watcher()
    w.add_ignore_rule('*.swp')
    w.add_ignore_rule('~*')
    w.add_ignore_rule('.*')
    files = ['a.js', 'b.swp', '~temp', '.DS_Store', 'src/c.js']
    filtered = w.scan_once(files)
    assert filtered == ['a.js', 'src/c.js']
    # add filter plugin to exclude dist/
    w.register_plugin('filter', lambda f: not f.startswith('dist/'))
    files2 = ['dist/file.js', 'src/app.js']
    filtered2 = w.scan_once(files2)
    assert filtered2 == ['src/app.js']

def test_transformer_and_sink_plugins():
    w = Watcher()
    # transformer: uppercase file path
    w.register_plugin('transformer', lambda f: f.upper())
    # sink: prefix
    w.register_plugin('sink', lambda f: f"processed:{f}")
    files = ['x.js', 'y.css']
    filtered = w.scan_once(files)
    assert set(filtered) == set(files)
    # check transformations
    assert ('x.js', 'X.JS') in w.last_transformed
    assert ('y.css', 'Y.CSS') in w.last_transformed
    # check sinks
    assert ('x.js', 'processed:x.js') in w.last_sunk
    assert ('y.css', 'processed:y.css') in w.last_sunk

def test_thread_pool_size():
    w = Watcher()
    assert w.thread_pool_size == 1
    w.set_thread_pool_size(5)
    assert w.thread_pool_size == 5
    with pytest.raises(ValueError):
        w.set_thread_pool_size(0)

def test_configure_logging():
    w = Watcher()
    w.configure_logging(level='DEBUG', fmt='%(msg)s', destination='stdout')
    assert w.log_config == {
        'level': 'DEBUG',
        'format': '%(msg)s',
        'destination': 'stdout'
    }

def test_handler_timeout_and_throttle_rate():
    w = Watcher()
    w.set_handler_timeout(10)
    assert w.handler_timeout == 10
    with pytest.raises(ValueError):
        w.set_handler_timeout(-1)
    w.set_throttle_rate(0.5)
    assert w.throttle_rate == 0.5
    with pytest.raises(ValueError):
        w.set_throttle_rate(-0.1)

def test_generate_change_summary():
    w = Watcher()
    # first call, no last build files
    summary1 = w.generate_change_summary(['a.js', 'b.js'])
    assert summary1 == "Files changed since last build: 2"
    # same files, no changes
    summary2 = w.generate_change_summary(['a.js', 'b.js'])
    assert summary2 == "Files changed since last build: 0"
    # one new, one removed
    summary3 = w.generate_change_summary(['b.js', 'c.js'])
    assert summary3 == "Files changed since last build: 2"

def test_move_detection_and_ignore_rules_flag():
    w = Watcher()
    assert not w.move_detection
    w.enable_move_detection()
    assert w.move_detection
    # ignore rules already tested above

def test_get_metrics_without_start():
    w = Watcher()
    assert w.get_metrics() is None
