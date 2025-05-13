import logging
from filewatcher.watcher import AsyncFileWatcher

def test_default_logger():
    w = AsyncFileWatcher(paths=[], includes=[])
    assert w.logger.name == "AsyncFileWatcher"
    # test changing logger
    custom = logging.getLogger("custom")
    w2 = AsyncFileWatcher(paths=[], includes=[], logger=custom)
    assert w2.logger is custom
