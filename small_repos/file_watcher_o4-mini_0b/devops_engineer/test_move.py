import asyncio
import pytest
import os
from filewatcher.watcher import AsyncFileWatcher

@pytest.mark.asyncio
async def test_move_event(tmp_path):
    file1 = tmp_path / "a.txt"
    file1.write_text("data")
    events = []
    watcher = AsyncFileWatcher(paths=[str(tmp_path)], includes=["*.txt"], interval=0.1)
    watcher.register_handler(lambda e: events.append(e))
    await watcher.start()
    # rename file
    file2 = tmp_path / "b.txt"
    os.rename(file1, file2)
    await asyncio.sleep(0.2)
    await watcher.stop()
    types = [e["type"] for e in events]
    # move is seen as deleted + created
    assert "deleted" in types and "created" in types
