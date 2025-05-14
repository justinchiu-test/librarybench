import os
import time
import tempfile
from config_manager.watcher import ConfigWatcher

def test_watcher(tmp_path):
    file_path = tmp_path / "cfg.yml"
    file_path.write_text("initial")
    events = []
    def cb(path):
        events.append(path)
    watcher = ConfigWatcher(str(file_path), cb, interval=0.05)
    watcher.start()
    time.sleep(0.1)
    file_path.write_text("changed")
    time.sleep(0.2)
    watcher.stop()
    assert len(events) >= 1
    assert events[0] == str(file_path)
