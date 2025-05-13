import asyncio
import tempfile
import os
import pytest
from filewatcher.watcher import AsyncFileWatcher

@pytest.mark.asyncio
async def test_non_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    file1 = tmp_path / "root.txt"
    file2 = sub / "sub.txt"
    events = []
    watcher = AsyncFileWatcher(paths=[str(tmp_path)], includes=["*.txt"], recursive=False, interval=0.1)
    watcher.register_handler(lambda e: events.append(e))
    await watcher.start()
    file1.write_text("r")
    file2.write_text("s")
    await asyncio.sleep(0.2)
    await watcher.stop()
    paths = [e["path"] for e in events]
    assert str(file1) in paths
    assert str(file2) not in paths
