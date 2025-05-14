import tempfile
import time
from config_manager.api import ConfigManager

def test_watch_file(tmp_path):
    f = tmp_path / "watch.txt"
    f.write_text("hello")
    called = []
    def cb():
        called.append(True)
    cm = ConfigManager(dev_mode=True)
    cm.watch_config_file(str(f), cb)
    time.sleep(0.2)
    f.write_text("world")
    time.sleep(0.3)
    cm.stop_watch()
    assert any(called)
