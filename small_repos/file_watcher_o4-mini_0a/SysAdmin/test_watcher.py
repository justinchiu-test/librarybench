import os
from audit_watcher.watcher import Watcher, Event
from audit_watcher.symlink import SymlinkConfig
from audit_watcher.history import EventHistoryStore
from audit_watcher.plugins import CICDPluginManager
from audit_watcher.handlers import HandlerRegistry
from audit_watcher.filters import HiddenFileFilter
from audit_watcher.throttler import Throttler
import tempfile

def test_watcher_pipeline(tmp_path):
    # setup
    history = EventHistoryStore(str(tmp_path), max_bytes=1024, backup_count=1)
    plugins = CICDPluginManager()
    handlers = HandlerRegistry()
    hidden = HiddenFileFilter("exclude")
    throttler = Throttler(limit_per_second=10)
    syc = SymlinkConfig(False)
    watcher = Watcher("/tmp", syc, history, plugins, handlers, hidden, throttler, dry_run=False)
    # register handler and plugin
    h_calls = []
    p_calls = []
    handlers.register("create", "/tmp/", lambda e: h_calls.append(e.src_path))
    plugins.register(lambda e: p_calls.append(e.event_type))
    # emit visible event
    e = Event("create", "/tmp/file.txt")
    result = watcher.emit_event(e)
    assert result is True
    assert h_calls == ["/tmp/file.txt"]
    assert p_calls == ["create"]
    # check history log
    log_file = tmp_path / "events.log"
    content = log_file.read_text()
    assert "create,/tmp/file.txt," in content

def test_watcher_dry_run(tmp_path):
    history = EventHistoryStore(str(tmp_path), max_bytes=1024, backup_count=1)
    plugins = CICDPluginManager()
    handlers = HandlerRegistry()
    hidden = HiddenFileFilter("all")
    throttler = Throttler(limit_per_second=10)
    syc = SymlinkConfig(False)
    watcher = Watcher("/tmp", syc, history, plugins, handlers, hidden, throttler, dry_run=True)
    h_calls = []
    p_calls = []
    handlers.register("delete", "/tmp/", lambda e: h_calls.append(e.src_path))
    plugins.register(lambda e: p_calls.append(e))
    e = Event("delete", "/tmp/file")
    result = watcher.emit_event(e)
    assert result is True
    assert h_calls == ["/tmp/file"]
    # in dry-run, plugin and history skipped
    assert p_calls == []
    assert not (tmp_path / "events.log").exists()
