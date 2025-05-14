import logging
import os
from etl_watcher import (
    FileWatcher, watcher,
    start_metrics_endpoint, scan_once, register_plugin,
    set_thread_pool_size, configure_logging,
    set_handler_timeout, set_throttle_rate,
    generate_change_summary, enable_move_detection, add_ignore_rule,
)

def test_start_metrics_endpoint_instance():
    fw = FileWatcher()
    assert not fw.metrics_started
    fw.start_metrics_endpoint(9001)
    assert fw.metrics_started
    assert fw.metrics_port == 9001

def test_start_metrics_endpoint_module():
    watcher.metrics_started = False
    start_metrics_endpoint(9100)
    assert watcher.metrics_started
    assert watcher.metrics_port == 9100

def test_scan_once(tmp_path):
    test_dir = tmp_path / "data"
    test_dir.mkdir()
    file_path = test_dir / "file.txt"
    file_path.write_text("sample")
    result = scan_once(str(test_dir))
    assert isinstance(result, list)

def test_register_plugin_instance():
    fw = FileWatcher()
    def dummy_plugin(): pass
    fw.register_plugin("dummy", dummy_plugin)
    assert "dummy" in fw.plugins
    assert fw.plugins["dummy"] is dummy_plugin

def test_register_plugin_module():
    watcher.plugins.clear()
    def mod_plugin(): pass
    register_plugin("mod", mod_plugin)
    assert "mod" in watcher.plugins
    assert watcher.plugins["mod"] is mod_plugin

def test_set_thread_pool_size_instance():
    fw = FileWatcher()
    fw.set_thread_pool_size(5)
    assert fw.thread_pool_size == 5

def test_set_thread_pool_size_module():
    set_thread_pool_size(8)
    assert watcher.thread_pool_size == 8

def test_configure_logging():
    # Reset logging level to NOTSET
    logging.root.setLevel(logging.NOTSET)
    configure_logging(logging.DEBUG, fmt="%(message)s")
    assert logging.root.level == logging.DEBUG

def test_set_handler_timeout_instance():
    fw = FileWatcher()
    fw.set_handler_timeout(30)
    assert fw.handler_timeout == 30

def test_set_handler_timeout_module():
    set_handler_timeout(45)
    assert watcher.handler_timeout == 45

def test_set_throttle_rate_instance():
    fw = FileWatcher()
    fw.set_throttle_rate(100)
    assert fw.throttle_rate == 100

def test_set_throttle_rate_module():
    set_throttle_rate(200)
    assert watcher.throttle_rate == 200

def test_generate_change_summary_instance():
    fw = FileWatcher()
    summary = fw.generate_change_summary(120, 5)
    assert summary == "120 files ingested, 5 failed validation"

def test_generate_change_summary_module():
    summary = generate_change_summary(10, 2)
    assert summary == "10 files ingested, 2 failed validation"

def test_enable_move_detection_instance():
    fw = FileWatcher()
    assert not fw.move_detection
    fw.enable_move_detection()
    assert fw.move_detection

def test_enable_move_detection_module():
    watcher.move_detection = False
    enable_move_detection()
    assert watcher.move_detection

def test_add_ignore_rule_instance():
    fw = FileWatcher()
    fw.add_ignore_rule("*.tmp")
    assert "*.tmp" in fw.ignore_rules

def test_add_ignore_rule_module():
    watcher.ignore_rules.clear()
    add_ignore_rule(".*")
    assert ".*" in watcher.ignore_rules
